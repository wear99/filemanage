from parts.read_excel import read_design_BOM, rule
from parts.models import Change
from parts.update import all_code
from parts.search import sort_by_sn,parent_sn,get_bom_model
import re

#-------------------写入bom库----------------------------------
def update_change_model(bom, ar_id, add_time):
    new_bom = []
    for item in bom:
        # 统一添加到数据库
        new = Change()
        new.archive = ar_id
        new.sn = item.get['sn']
        new.parent = item.get['parent']

        new.draw = item.get('draw')
        new.name = item.get('name')
        new.before_code = item.get('before_code')
        new.after_code = item.get('after_code')
        new.before_des = item.get('before_des')
        new.after_des = item.get('after_des')
        new.change_type = item.get('change_type')
        new.change_draw = item.get("change_draw")
        new.stock = item.get('stock')
        new.on_order = item.get('on_order')
        new.suggestion = item.get('suggestion')
        new.product = item.get('product')
        new.add_time = add_time

        new_bom.append(new)

    if new:  # 批量创建
        Change.objects.filter(archive=ar_id).delete()   # 先删除旧的发放单bom
        Change.objects.bulk_create(new_bom)


#-----------------更新入口程序------------------------------------
def import_changes(fpath, ar_obj, add_time):
    rst = read_design_BOM(fpath, type='CHANGE')
    if 'error' in rst:
        return rst
    elif 'bom' in rst:
        # 将更新bom写入库中
        ar_id = str(ar_obj.archive_id)
        update_change_model(rst['bom'], ar_id, add_time)



#-------------------查询---------------------------------
#查找更改条目(字典)的子项
def change_child(search,ar_id=None):
    query = get_bom_model('CHANGE', ar_id)

    if search=='ROOT' and ar_id:
        objs = query.filter(parent='ROOT').values()
    else:
        obj_1=query.filter(sn=search)
        obj_2 = query.filter(
            sn__istartswith=search+'.')
        objs=obj_1|obj_2

    bom = []    
    for obj in objs.values():
        bom.append(obj)
    
    bom.sort(key=sort_by_sn)

    return bom


#查找更改条目的父项
def change_parent(search, ar_id=None):
    psn=parent_sn(search)
    query = get_bom_model('CHANGE', ar_id)

    objs = query.filter(sn__in=psn).values()

    bom = []    
    for obj in objs:
        bom.append(obj)

    bom.sort(key=sort_by_sn)

    return bom


# 查找设计更改条目
def change_find(search,draw=None,ar_id=None):
    query = get_bom_model('CHANGE', ar_id)

    if search=='ROOT':
        query=query.filter(parent='ROOT')
            
    bom=[]
    
    if not draw and search in all_code:
        draw = all_code[search]
    
    if 'GB' in draw or 'JB' in draw:
        draw = ''

    if draw:
        # 去除图号中括号内容
        draw = re.sub("（", '(', draw)
        draw = re.sub("）", ')', draw)
        draw = re.sub("\(.*\)", '', draw)

    for item in query.values():
        if search in str(item.values()):            
            bom.append(item)
        elif draw and draw in str(item.values()):
            bom.append(item)

    return bom
