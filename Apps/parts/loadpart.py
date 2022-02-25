from .models import ArchiveBom, PartCode, CurrentBom, ErpBom

#----------初始化：物料表、BOM表-----------------


def load_code():    
    all = {}
    q = PartCode.objects.all().values()
    for item in q:
        item['add_time'] = item['add_time'].strftime("%Y-%m-%d")
        all[item['code']] = item

    return all


# 不用
def load_currentbom():
    parent = {}
    child = {}
    qs = CurrentBom.objects.all().values()
    for item in qs:
        if item['parent'] not in child:
            child[item['parent']] = [item]
        else:
            child[item['parent']].append(item)

        if item['child_id'] not in parent:
            parent[item['child_id']] = [item]
        else:
            parent[item['child_id']].append(item)

    return parent, child


def load_bom(query):  #分当前和历史
    
    parent = {}
    child = {}
    bom = {}
    for item in query:
        #item['add_time'] = item['add_time'].strftime("%Y-%m-%d")

        # 生成历史bom
        if item['archive'] not in bom:
            bom[item['archive']] = [item]
        else:
            bom[item['archive']].append(item)

        #生成child 当前bom
        if item['parent'] not in child:
            child[item['parent']] = [item]
        else:
            if item['archive'] == child[
                    item['parent']][-1]['archive']:  #当处于同一个bom时
                if item not in child[item['parent']]:
                    child[item['parent']].append(item)

            else:  #当处于不同Bom时,只能留存一个。先比较类型：小批的优先度最高，同优先度再比较时间
                if item['parent'] == 'ROOT':
                    child[item['parent']].append(item)
                else:
                    if item['bom_type'] > child[
                            item['parent']][-1]['bom_type']:
                        child[item['parent']] = [item]
                    elif item['bom_type'] == child[
                            item['parent']][-1]['bom_type']:
                        if item['add_time'] > child[
                                item['parent']][-1]['add_time']:
                            child[item['parent']] = [item]

    parent_key = {}
    #生成parent 当前bom
    for c in child.values():
        for item in c:
            if item['child_id'] not in parent:
                parent[item['child_id']] = [item]
                parent_key[item['child_id']] = [item['parent']]
            else:
                if item['parent'] not in parent_key[item['child_id']]:
                    parent[item['child_id']].append(item)
                    parent_key[item['child_id']].append(item['parent'])

    return parent, child, bom


def load_archivebom():
    query = ArchiveBom.objects.all().values()
    return load_bom(query)


def load_erpbom():  #分当前和历史结构
    query = ErpBom.objects.all().values()
    return load_bom(query)


all_code = {}
parent_arbom = {}  # 用于正向查询，key是父项，value是子项
child_arbom = {}  # 用于正向查询，key是父项，value是子项
archive_bom = {}
erp_bom = {}
parent_erpbom = {}
child_erpbom = {}

#all_code = load_code()
#parent_bom, child_bom = load_currentbom()
#parent_arbom, child_arbom, archive_bom = load_archivebom()
#parent_erpbom, child_erpbom, erp_bom = load_erpbom()