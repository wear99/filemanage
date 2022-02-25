from parts.models import PartCost
from parts.read_excel import read_design_BOM

# ----------初始化：所有成本表-----------


def load_cost():
    all = {}
    old={}
    q = PartCost.objects.all().values()
    for item in q:
        item['add_time'] = item['add_time'].strftime("%Y-%m-%d")
        if item['code'] not in all:
            all[item['code']] = item
        else:
            if item['code'] not in old:
                old[item['code']]=[]

            if item['add_time']>all[item['code']]['add_time']:                
                old[item['code']].append(all[item['code']])
                all[item['code']] = item
            else:
                old[item['code']].append(item)

    return all,old


all_cost = {}
#all_cost,old_cost = load_cost()


# ----------------更新成本库--------------

def creat_cost_dict(bom, add_time):  # 去掉重复和无成本项
    new = {}
    for item in bom:
        if item['cost'] > 0.01:
            item['add_time'] = add_time
            new[item['code']] = item
    return new


def creat_change(bom_dict):  # 与成本库对比，创建new、old
    new = []
    old = []
    change = []
    for key, item in bom_dict.items():
        item['cost_valid'] = 1
        if key not in all_cost:
            new.append(item)
        else:
            if abs(item['cost'] - all_cost[key]['cost']) > 1:
                if item['add_time'] < all_cost[key]['add_time']:  # 导入日期和原成本日期对比，决定哪个成本作为最新成本
                    item['cost_valid'] = 0
                else:
                    old.append(all_cost[key])     # 成本已变化的，需要对数据内字段备注更改为old

                new.append(item)

                change.append(all_cost[key])
                change.append(item)

    return new, old, change


def update_cost_model(new, old):  # 将结果写入成本库
    if new:
        new_cost = []
        for item in new:
            c = PartCost()
            c.code = item['code']
            c.material_cost = item['material_cost']
            c.labor_cost = item['labor_cost']
            c.managed_cost = item['managed_cost']
            c.cost = item['cost']
            c.add_time = item['add_time']
            c.cost_valid = item['cost_valid']
            new_cost.append(c)

        PartCost.objects.bulk_create(new_cost)

    if old:
        old_id = []
        for item in old:
            old_id.append(item['id'])

        PartCost.objects.filter(id__in=old_id).update(cost_valid=0)

# 入口
def import_upload_cost(fpath, add_time):  # 更新上传的成本库:先读取，再对比已有的，再写入,最后刷新内存中的成本数据
    rst = read_design_BOM(fpath, type='COST')
    if 'error' in rst:
        return rst

    bom_dict = creat_cost_dict(rst['bom'], add_time)
    new, old, change = creat_change(bom_dict)
    update_cost_model(new, old)

    global all_cost,old_cost
    all_cost,old_cost = load_cost()

    return {'ok': "", 'total': len(bom_dict), 'new': len(new), 'change': len(change), 'data': change}


# ------------------查找成本库----------------
def bom_add_cost(bom): #在库中查找,只显示最新成本数据
    codes={}
    for item in bom:
        codes[item['code']]=''
    
    costs=PartCost.objects.filter(code__in=list(codes.keys())).order_by('add_time').values()
    cost_d={}
    for cost in costs:
        cost_d[cost['code']]=cost
    
    for item in bom:
        code = item['code']
        if code in cost_d:
            item['material_cost'] = round(cost_d[code]['material_cost'], 2)
            item['labor_cost'] = round(cost_d[code]['labor_cost'], 2)
            item['managed_cost'] = round(cost_d[code]['managed_cost'], 2)
            item['cost'] = round(cost_d[code]['cost'], 2)
            item['add_time'] = str(cost_d[code]['add_time'].strftime("%Y-%m-%d"))
        else:
            item['material_cost'] = 0
            item['labor_cost'] = 0
            item['managed_cost'] = 0
            item['cost'] = 0
            item['add_time'] = ''

        if 'quantity' in item and isinstance(item['quantity'], (int, float)):
            item['total_cost'] = round(item['cost'] * item['quantity'], 2)
        else:
            item['total_cost'] = 0

    return bom


def bom_add_cost_dict(bom):   #内存中查找
    for item in bom:
        code = item['code']
        if code in all_cost:
            item['material_cost'] = round(all_cost[code]['material_cost'], 2)
            item['labor_cost'] = round(all_cost[code]['labor_cost'], 2)
            item['managed_cost'] = round(all_cost[code]['managed_cost'], 2)
            item['cost'] = round(all_cost[code]['cost'], 2)
            item['add_time'] = str(all_cost[code]['add_time'])
        else:
            item['material_cost'] = 0
            item['labor_cost'] = 0
            item['managed_cost'] = 0
            item['cost'] = 0
            item['add_time'] = ''

        if 'quantity' in item and isinstance(item['quantity'], (int, float)):
            item['total_cost'] = round(item['cost'] * item['quantity'], 2)
        else:
            item['total_cost'] = 0

    return bom


def find_cost_history(code_list):
    codes = {}
    for item in code_list:
        codes[item['code']] = ''

    costs = PartCost.objects.filter(code__in=list(
        codes.keys())).order_by('add_time').values()
    
    bom=[]
    for item in code_list:
        code = item['code']
        has_cost=False
        for cost_d in costs:
            if code == cost_d['code']:
                has_cost = True
                item['material_cost'] = round(cost_d[code]['material_cost'], 2)
                item['labor_cost'] = round(cost_d[code]['labor_cost'], 2)
                item['managed_cost'] = round(cost_d[code]['managed_cost'], 2)
                item['cost'] = round(cost_d[code]['cost'], 2)
                item['add_time'] = str(
                    cost_d[code]['add_time'].strftime("%Y-%m-%d"))

                bom.append(item.copy())

        if not has_cost:
            bom.append(item)
            
    return bom



def bom_recalc_cost(bom):  # 重新按层级计算成本，把本项成本累加到父项下面    
    pcost = {}
    bom.reverse()

    for item in bom:
        # 先检查是否有累加结果，再进行对比
        if item['code'] in pcost:
            pmat = pcost[item['code']]['material_cost']
            plab = pcost[item['code']]['labor_cost']
            pman = pcost[item['code']]['managed_cost']

            # 对于焊接件下面只有原材料和材料成本，没有人工成本。所以只有子件有该项成本的才赋值，没有的用原来的。
            if pmat:
                item['material_cost'] = pmat
            if plab:
                item['labor_cost'] = plab
            if pman:
                item['managed_cost'] = pman

            pc = item['material_cost'] + \
                item['labor_cost']+item['managed_cost']

            if abs(pc-item['cost'])>1:
                item['remark'] = '{0}导入:{1}'.format(
                    str(item['add_time']), str(item['cost']))
                item['cost'] = pc
                item['total_cost'] = item['cost']*item['total']

        # 再把自己的成本累加到父项下面，防止同一个父项的重复累加，要进行key判断
        if item['parent'] not in pcost:
            pcost[item['parent']] = {'material_cost': 0,
                                     'labor_cost': 0, 'managed_cost': 0, 'cost': 0,'child':[]}
        elif item['code'] not in pcost[item['parent']]['child']:
            pcost['material_cost'] += item['material_cost']*item['quantity']
            pcost['labor_cost'] += item['labor_cost']*item['quantity']
            pcost['managed_cost'] += item['managed_cost']*item['quantity']
            pcost['cost'] += pcost['material_cost'] + \
                pcost['labor_cost']+pcost['managed_cost']
            
            pcost[item['parent']]['child'].append(item['code'])            

        bom.reverse()
    return bom
