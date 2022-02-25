from parts.models import Change
from parts.models import PartCode, ArchiveBom, CurrentBom, ErpBom
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone
from parts.update import all_code, parent_arbom, child_arbom, parent_erpbom, child_erpbom
import re
from parts.read_excel import rule
from archive.method import archivefind

# 反查、子件时只在最新结构(ebom、erpbom)中查询；
# 如果要查历史结构，另外查询
# 发放bom 应按每次输出的bom查询，不用最新的。图纸结构时可找时间最后的

# erp bom则分最新和导入的；


def time_log(func):
    def wrapper(*args, **kvargs):
        s_time = timezone.now()         # ----->函数运行前时间
        res = func(*args, **kvargs)
        print("%s消耗时间为:%s" % (func.__name__, timezone.now()-s_time))
        return res
    return wrapper  # ---->装饰器其实是对闭包的一个应用


def bom_add_total(bom):  # 根据parent属性添加total
    num = {'ROOT': 1}
    new = []
    for item in bom:
        if item['parent'] not in num:
            item['parent'] = 'ROOT'

        item['total'] = item['quantity']*num[item['parent']]
        num[item['child_id']] = item['total']

        new.append(item)

    return new


def bom_add_sn(bom):  # 根据parent属性添加sn
    new = []
    sn = {'ROOT': ''}
    no = {'ROOT': 1}
    for item in bom:
        if item['parent'] not in sn:
            item['parent'] = 'ROOT'

        item['sn'] = sn[item['parent']]+str(no[item['parent']])
        no[item['parent']] += 1  # 对父项顺序加1

        sn[item['child_id']] = item['sn']+'.'
        no[item['child_id']] = 1  # 将子项的顺序号重置为1

        new.append(item)

    return new


def bom_add_pid(bom):  # 对排好序的bom，根据parent字段 添加lv 和pid
    pid = {'ROOT': 'ROOT'}
    lv = {'ROOT': 0}
    new = []
    for item in bom:
        if item['parent'] not in pid:
            item['parent'] = 'ROOT'

        item['pid'] = pid[item['parent']]
        item['lv'] = lv[item['parent']]+1

        lv[item['child_id']] = item['lv']
        pid[item['child_id']] = item['id']

        new.append(item)

    return new


def part_add_info(bom):
    for item in bom:
        if item['child_id'] in all_code:
            item.update(all_code[item['child_id']])

    return bom


# -----------------part库查找----------------------
def Partfind(type, search, opt):  # 物料查找方法
    qset = Q()
    for i, item in enumerate(search):
        if type == 'code':
            q = Q(code__icontains=item)
        elif type == 'draw':
            q = Q(draw__icontains=item)
        elif type == 'partname':
            q = Q(name__icontains=item)
        elif type == 'remark':
            q = Q(remark__icontains=item)
        else:
            q = Q(code__icontains=item) | Q(
                draw__icontains=item) | Q(name__icontains=item) | Q(material__icontains=item) | Q(remark__icontains=item)

        if opt == 'OR':
            qset = qset | q
        else:
            qset = qset & q
    queryset = PartCode.objects.filter(qset).order_by()

    parts = []
    for obj in queryset:
        item = model_to_dict(obj)
        item['add_time'] = obj.add_time.strftime("%Y-%m-%d")
        if obj.file:
            item['file_id'] = obj.file.file_id
        parts.append(item)

    return parts


# ------------------发放bom 数据库（历史数据）查找------------

def sort_by_sn(item):
    '先将序号转为列表，再转为数字格式，再进行排序'
    sn = item['sn'].split('.')

    return [int(x) for x in sn if x]


def parent_sn(sn):
    s = ''
    parent_sn=[]
    for n in sn.split("."):  # 拼接父项的sn号码
        if not n:
            continue
        if s:
            s = s+'.'+str(n)
        else:
            s = str(n)
        parent_sn.append(s)

    return parent_sn



def get_bom_model(bom_type='ARCHIVE',ar_id=None):
    if bom_type == "ARCHIVE":
        query = ArchiveBom.objects.all()
    elif bom_type == "ERPBOM":
        query = ErpBom.objects.all()
    elif bom_type=='CHANGE':
        query=Change.objects.all()

    if ar_id:
        query = query.filter(archive=ar_id)
    
    return query



def childfind_model(code,bom_type,ar_id=None):        
    query = get_bom_model(bom_type, ar_id)

    if ar_id and code=='ROOT':
        objs=query.filter(parent='ROOT').values()
    else:
        objs = query.filter(child=code).values()

    if not objs:
        return

    ar = {}
    for obj in objs:
        ar[obj['archive']] = obj

    bom = []
    for key, item in ar.items():
        queryset = query.filter(
            sn__istartswith=item['sn']+'.', archive=key).values()

        b = []
        b.append(item)
        for o in queryset:
            b.append(o)

        b.sort(key=sort_by_sn)
        bom = bom+b

    bom = bom_add_pid(bom)
    bom = bom_add_sn(bom)
    bom = bom_add_total(bom)
    bom = part_add_info(bom)

    return bom



def parentfind_model(code, bom_type,ar_id=None):
    query = get_bom_model(bom_type, ar_id)
    
    objs = query.filter(child=code).values()
    if not objs:
        return []

    ar = {}
    for obj in objs:
        if obj['archive'] not in ar:
            ar[obj['archive']] = []
        
        ar[obj['archive']]=parent_sn(obj['sn'])

    bom = []
    for key, item in ar.items():
        queryset = query.filter(
            archive=key, sn__in=item).values()

        b = []
        for item in queryset:
            b.append(item)
        b.sort(key=sort_by_sn)
        bom = bom+b

    bom = bom_add_pid(bom)
    bom = bom_add_sn(bom)
    bom = bom_add_total(bom)
    bom = part_add_info(bom)
    return bom



# -----------------------Root查找-------------------------
def rootfind(search, field_type, bom_type):  # 查询Bom结构：发放单号、机型、类型、root id
    def get_ar_list(s, type):
        ar_obj = archivefind(s, type)
        ar_list = [item['archive_id'] for item in ar_obj]
        return ar_list

    query = get_bom_model(bom_type)
    
    if field_type in ('ARCHIVE_NO', 'PRODUCT_NAME', 'PRODUCT_CODE', 'USERNAME'):
        query = query.filter(archive__in=get_ar_list(search, field_type))
    elif field_type == 'ARCHIVE_ID':
        query = query.filter(archive=search)
    elif field_type == 'CODE':
        query = query.filter(child_id=search)

    query = query.filter(parent__in=('ROOT', 'root')
                       ).order_by('child_id').values()
    bom = []
    for item in query:
        bom.append(item)

    bom = bom_add_pid(bom)
    bom = bom_add_sn(bom)
    bom = part_add_info(bom)

    return bom



# ------------------当前bom数据库 递归查找,不用-----------------

def Childfind_Current1111(code):  # 递归查询
    def find_child(cd, n):
        cids = all.filter(parent=cd)
        for item in cids:
            # item=obj.to_dict()
            item['lv'] = n
            item['code'] = item['child_id']
            bom.append(item)
            find_child(item['code'], n+1)

    bom = []

    p1 = CurrentBom.objects.filter(child__code=code).last()
    if p1:
        item = p1.to_dict()
        item['lv'] = 1
        item['parent'] = 'root'
        bom.append(item)
        print("递归开始："+str(timezone.now()))
        find_child(code, 2)
        print(len(bom))
        print("递归结束："+str(timezone.now()))
        #bom = bom_add_total(bom)
        #bom = bom_add_sn(bom)
        #bom = bom_add_pid(bom)

    return bom


def Parentfind_Current1111(code):  # 递归查找
    def find_parent(cd, n):
        pids = CurrentBom.objects.filter(child_id=cd)
        #parent[n] = ''
        for obj in pids:
            item = obj.to_dict()
            item['lv'] = n
            parent.append(item)
            find_parent(obj.parent, n+1)

        # 当反查到尽头的时候,把这条路径上的父项都添加到一起，并重置parent
        if parent:
            key = ''
            parent.reverse()
            for i, item in enumerate(parent):
                item['lv'] = i+1
                key += item['parent']

            bom_dict[key] = parent[:]
            parent.clear()
            # bom.append(new)

    def format_bom():
        keys = list(bom_dict.keys())
        keys.sort()
        lv = {1: ''}
        for key in keys:
            for item in bom_dict[key]:
                if lv[item['lv']] != item['code']:
                    bom.append(item)
                    lv[item['lv']] = item['code']
                    for n in range(item['lv'] + 1, 8):
                        lv[n] = ''
                else:
                    # 已存在，所以跳过
                    pass

    bom = []
    bom_dict = {}
    parent = []
    print("递归开始："+str(timezone.now()))
    find_parent(code, 1)
    print("递归结束："+str(timezone.now()))
    format_bom()
    bom = bom_add_total(bom)
    bom = bom_add_sn(bom)
    bom = bom_add_pid(bom)

    return bom


# -----------------bom 内存（最新数据）查找----------------------

def Partfind_dict(search, field_type, opt='AND'):  # 物料查找方法
    rst_code = []
    field_type = field_type.lower()
    for item in all_code.values():
        tar = False
        if field_type == 'all':
            ss = str(item.values())
        elif field_type in item and item[field_type]:
            ss = str(item[field_type])
        else:
            continue

        for x in search:
            if x in ss:
                tar = True
                if opt == 'OR':
                    break
            else:
                tar = False
                if opt == 'AND':
                    break
        if tar:
            rst_code.append(item)
    return rst_code


@time_log
def childfind_current(code, bom_type='ARCHIVE'):  # 递归查询
    def find_child(cd, n):
        if cd in child_bom:
            for item in child_bom[cd]:
                item['lv'] = n
                bom.append(item)
                find_child(item['child_id'], n+1)

    if bom_type == 'ARCHIVE':
        child_bom = child_arbom
    elif bom_type == 'ERPBOM':
        child_bom = child_erpbom
    else:
        return []

    bom = []
    if code in child_bom:
        item = {}
        item['lv'] = 1
        item['id'] = 0
        item['parent'] = 'ROOT'
        item['child_id'] = code
        item['quantity'] = 1

        bom.append(item)
        find_child(code, 2)

        bom = bom_add_total(bom)
        bom = bom_add_sn(bom)
        bom = bom_add_pid(bom)
        bom = part_add_info(bom)

    return bom


@time_log
def parentfind_current(code, bom_type='ARCHIVE'):  # 递归查找
    def find_parent(cd, n):
        if cd in parent_bom:
            for item in parent_bom[cd]:
                item['lv'] = n
                parent[n] = item  # 重要！ 不能用列表，必须要层次覆盖

                find_parent(item['parent'], n-1)

        # 当反查到尽头的时候,把这条路径上的父项都添加到一起，并重置parent
        else:
            if n == 8:
                return

            key = ''
            b = []
            for i, m in enumerate(range(n+1, 10)):
                parent[m]['lv'] = i+1
                key += parent[m]['parent']
                b.append(parent[m].copy())

            bom_dict[key] = b[:]

    def format_bom():
        keys = list(bom_dict.keys())
        keys.sort()
        lv = {1: ''}
        for key in keys:
            for item in bom_dict[key]:
                if lv[item['lv']] != item['child_id']:
                    bom.append(item)
                    lv[item['lv']] = item['child_id']

                    for n in range(item['lv'] + 1, 8):
                        lv[n] = ''
                else:
                    # 已存在，所以跳过
                    pass

    if bom_type == 'ARCHIVE':
        parent_bom = parent_arbom
    elif bom_type == 'ERPBOM':
        parent_bom = parent_erpbom
    else:
        return []

    bom = []
    bom_dict = {}
    parent = {}

    find_parent(code, 9)
    format_bom()

    bom = bom_add_total(bom)
    bom = bom_add_sn(bom)
    bom = bom_add_pid(bom)
    bom = part_add_info(bom)

    return bom


# 返回给定编码的所有版本列表
def partHistoryFind(code):
    if code not in all_code:
        return []

    if not re.match(rule['code'], code):
        if code in all_code:
            return [all_code[code]]

    code_his = []
    draw=all_code[code]['draw']
    
    if 'GB' in draw or 'JB' in draw:
        draw=''
    else:
        # 去除图号中括号内容
        draw = re.sub("（", '(', draw)
        draw = re.sub("）", ')', draw)

        draw = re.sub("\(.*\)", '', draw)        

    for key in all_code:
        if re.match(rule['code'], key): 
            if key.startswith(code[:-1]):
                code_his.append(all_code[key])
            elif draw and all_code[key]['draw'] and draw in all_code[key]['draw']:
                code_his.append(all_code[key])        

    return code_his
