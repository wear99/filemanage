from parts.models import ArchiveBom, PartCode, CurrentBom,ErpBom
from files.models import ssFile
from django.utils import timezone
from parts.read_excel import read_design_BOM,rule
import re

from parts.loadpart import all_code, parent_erpbom, child_erpbom, erp_bom,load_code,load_archivebom,load_erpbom
#ArchiveBom.objects.all().delete()
#CurrentBom.objects.all().delete()



#----------写入物料库---------------------

def update_archive_partcode(bom,add_time):  # 更新发放bom中的物料库, 更新 材料，重量，备注，分工
    bom_dict={}
    new=[]
    update=[]
    for item in bom:
        # 使用字典去除重复的物料
        bom_dict[item['code']]=item

    for key, item in bom_dict.items():
        n=PartCode(code=key,name=item['name'],draw=item['draw'])
        n.add_time = add_time
        if key not in all_code:
            new.append(n)
        else:
            mk=False
            for i in ('material', 'weight', 'remark', 'division'):
                if item[i]!=all_code[key][i]:
                    mk = True
                    if item[i]:
                        pass
                    else:
                        item[i] = all_code[key][i]
            if mk:
                n.material = item['material']
                n.weight = item['weight']
                n.remark = item['remark']
                n.division = item['division']
                update.append(n)

    if new:
        PartCode.objects.bulk_create(new)
    if update:
        PartCode.objects.bulk_update(
            update, ['material', 'weight', 'remark', 'division','add_time'])


def update_batch_partcode(bom):  # 更新小批物料库,   更新 图号、名称
    new=[]
    update=[]
    rst={}
    for item in bom:
        np = PartCode()
        np.code = item['code']
        np.name = item['name']
        if item['draw']:
            np.draw = item['draw']
        if item['material']:
            np.material = item['material']
        if item['time']:
            np.add_time = item['time']

        if item['code'] in all_code:
            if item['name'] != all_code[item['code']]['name'] or item['draw'] != all_code[item['code']]['draw']:
                update.append(np)
        else:
            new.append(np)

    rst['total']=len(bom)
    if new:
        PartCode.objects.bulk_create(new)
        rst['new']=len(new)
    if update:
        PartCode.objects.bulk_update(update, ['name', 'draw', 'add_time'])
        rst['update']=len(update)

    return rst


def check_part_valid():
    codes=list(all_code.keys())
    codes.sort()
    old=[]
    for n,key in enumerate(codes[:-1]):
        if not re.match(rule['code'], key):
            continue

        if key[:-1]== codes[n+1][:-1]:
            if all_code[key]['part_valid']!=0:
                old.append(key)

    if old:
        PartCode.objects.filter(code__in=old).update(part_valid=0)


#---------------------写入图纸库--------------------------------

def update_file_output(bom,ar_id):   # 把Bom中分发部门写入文件库
    # 通过发放单号找出所有图纸，再和bom中图号比对
    bom_dict = {}
    for item in bom:
        # 使用字典去除重复的物料
        if item['draw'] and 'GB' not in item['draw'] and item['output']:
            bom_dict[item['draw']] = item['output']

    # 先找到所有bom图号的文件
    file_obj = ssFile.objects.filter(
        archive_id=ar_id, filename__in=list(bom_dict.keys()))

    for obj in file_obj:
        if obj.filename in bom_dict:
            obj.output = bom_dict[obj.filename]
            obj.save()


def part_file(ar_id,bom=None,filelist=None):   # 关联图纸和物料
    # 找到所有发放单物料或bom物料
    # 找到所有发放单物料或file列表
    # 对两者同图号的进行关联，写入物料表
    def get_part():
        bom_dict = {}
        if bom:
            for item in bom:
                bom_dict[item['code']] = item   # 使用字典去除重复的物料
            codes = list(bom_dict.keys())
            q_part = PartCode.objects.filter(code__in=codes)
        else:
            q_part = PartCode.objects.filter(
                archivebom__archive=ar_id)

        part_obj={}
        for obj in q_part:
            if obj.code in bom_dict:
                draw = bom_dict[obj.code]['draw']
            else:
                draw = obj.draw
            part_obj[draw]=obj

        return part_obj

    def get_file():
        if filelist:
            objs = ssFile.objects.filter(archive=ar_id,file_id__in=filelist)
        else:
            objs = ssFile.objects.filter(archive=ar_id)

        file_obj={}
        for obj in objs:
            file_obj[obj.pk] = obj

        return file_obj
    rst={}
    parts=get_part()
    files=get_file()

    if not (parts and files):
        return

    no_part=[]
    for key,file in files.items():
        if key in parts:
            parts[key].file_id=key
            parts[key].save()

            file.part = parts[key].code
            file.save()
        else:
            no_part.append(key)
    rst['no_part'] = no_part
    return rst


#-------------------写入bom库----------------------------------

def update_archivebom_model(bom, ar_id,bom_type, add_time):  #更新发放bom库，是否要把没有包含的子件带进去？

    new_bom=[]
    for item in bom:
        # 统一添加到数据库
        new=ArchiveBom()
        new.archive = ar_id
        new.sn=item['sn']
        new.parent = item['parent']
        new.child_id=item['code']
        new.quantity=item['quantity']
        new.bom_type= bom_type
        new.add_time=add_time
        new_bom.append(new)

    if new: #批量创建
        ArchiveBom.objects.filter(archive=ar_id).delete()   # 先删除旧的发放单bom
        ArchiveBom.objects.bulk_create(new_bom)


# 不用
def update_currentbom(bom, add_time):  # 更新当前Bom库
    # 分2种情况：增加或更改数量的，可以直接update create；
    # 对于要删除的，就要根据父项编码反向查找在bom中是否存在，不存在则进行删除

    pids = []
    items = {}
    for item in bom:
        if re.match(r'0[1234]R', item['code']):  # 对于子件是原材料的跳过
            continue
        else:
            pids.append(item['parent'])
            items[item['parent']+item['code']] = item

    qy = CurrentBom.objects.filter(parent__in=pids).exclude(parent='root')
    objs = {}
    for obj in qy:
        objs[obj.parent+obj.child.code] = obj

    # 正向对比，找出需要增加、更新的：
    for key, item in items.items():
        if key not in objs:
            new = CurrentBom(parent=item['parent'], child_id=item['code'],
                             quantity=item['quantity'], sort_key=item['sn'].split('.')[-1], add_time=add_time)
            new.save()

        elif item['quantity'] != objs[key].quantity:
            objs[key].quantity = item['quantity']
            objs[key].add_time = add_time
            objs[key].save()

    # 反向对比，找出需要删除的：
    for key, obj in objs.items():
        if key not in items:
            obj.delete()



def update_erpbom_model(bom,bom_type,add_time): # 更新erp bom库
    new_bom = []
    if 'root' == bom[0]['parent']:
        rootkey = bom[0]['code']+"#"+str(add_time.strftime("%Y-%m-%d"))
    else:
        return

    for item in bom:
        # 统一添加到数据库
        new = ErpBom()
        new.archive = rootkey
        new.sn = item['sn']
        new.parent = item['parent']
        new.child_id = item['code']
        new.quantity = item['quantity']
        new.bom_type=bom_type
        new.add_time = add_time
        new_bom.append(new)

    if new:  # 批量创建
        # 先删除旧的bom
        ErpBom.objects.filter(archive=rootkey).delete()
        ErpBom.objects.bulk_create(new_bom)


#-----------------更新入口程序------------------------------------

def import_archivebom(fpath, ar_obj, add_time):  # 读取发放单中的BOM，并更新BOM和part库
    rst = read_design_BOM(fpath, type='ARCHIVE')

    if 'error' in rst:
        return rst
    elif 'bom' in rst:
        # 更新物料库
        update_archive_partcode(rst['bom'],add_time)

        # 更新发放bom库
        ar_id=str(ar_obj.archive_id)
        bom_type=ar_obj.stage

        update_archivebom_model(rst['bom'], ar_id,bom_type, add_time)

        # 更新当前bom库
        #update_currentbom(rst['bom'], add_time)

        # 更新图纸库的发放和part属性
        update_file_output(rst['bom'], ar_id)

        # 图纸和物料进行关联
        part_file(bom=rst['bom'],ar_id=ar_id)

        # 更新内存物料字典
        global all_code, parent_bom, child_bom
        all_code=load_code()
        check_part_valid()

        parent_bom, child_bom = load_archivebom()

        return {'success':''}



def import_upload_parts(fpath,add_time):   # 更新上传的物料库，先读取，再写入
    rst = read_design_BOM(fpath, type='CODE')
    if 'bom' in rst:
        rst = update_batch_partcode(rst['bom'])

    elif 'error' in rst:
        pass

    global all_code
    all_code = load_code()
    check_part_valid()

    return rst


def import_upload_erpbom(fpath, add_time):  # 按发放bom格式,需检查全部有编码；
    rst = read_design_BOM(fpath, type='ARCHIVE')
    if 'error' in rst:
        return rst

    # 更新erp bom库
    update_erpbom_model(rst['bom'], add_time)

    # 更新当前bom库
    update_currentbom(rst['bom'], add_time)

    #重新读取全部erp bom
    global parent_erpbom, child_erpbom, erp_bom
    parent_erpbom, child_erpbom, erp_bom = load_erpbom()

    return {'success': ''}
