from sqlalchemy import true
from application.models import Application,ApplicationBom
from parts.read_excel import read_design_BOM
from parts.update import all_code,child_arbom
from files.methods import filefind
import zipfile

#判断一个图号是否应该有图纸
def part_has_file(draw):
    if not draw:
        return 
    elif 'GB' in draw.upper() or 'JB' in draw.upper():
        return
    elif '.' in draw and '-' in draw:
        return True
    else:
        return



# 查找有无此物料，并将子结构一并写入；
def get_parts_from_bom(bom, include_child):    
    def get_child(code,sn):
        if code in child_arbom:   # child_bom中key是父项,value是字段，里面parent=key，child_id为子项编码
            i=1
            for ch in child_arbom[code]:                
                ch['draw'] = all_code[ch['child_id']]['draw']

                if not part_has_file(ch['draw']):
                    continue

                ch['name'] = all_code[ch['child_id']]['name']
                ch['file_id'] = all_code[item['code']]['file_id']

                ch['code'] = ch['child_id']
                ch['part_id'] = ch['child_id']                
                ch['sn']=sn+"."+str(i)
                i+=1

                new.append(ch)
                get_child(ch['child_id'], ch['sn'])

    new=[]
    code_dict={}
    for item in bom:
        if item['code'] in all_code:
            item['part_id']=item['code']
            item['file_id'] = all_code[item['code']]['file_id']            

        new.append(item)
        if include_child:
            get_child(item['code'],item['sn'])

    return new

#-------------------------------------------------------------------------------------------
# 数据写入arr_bom库
def update_app_bom(app_id,bom):    
    app_bom=[]
    for item in bom:
        new=ApplicationBom()
        new.app_id = app_id
        new.sn=item['sn']
        
        new.code=item['code']
        new.draw=item['draw']
        new.name=item['name']
        
        #new.part_id = item.get('part_id',None)
        if item['file_id']:
            new.file_id = item['file_id']
            new.provider='Auto'
        
        app_bom.append(new)

    ApplicationBom.objects.filter(app_id=app_id).delete()
    ApplicationBom.objects.bulk_create(app_bom)


#检查申请图纸是否全部都有
def check_app_file(app_id):
    q = ApplicationBom.objects.filter(app_id=app_id)
    total_file = q.count()
    miss_file = q.filter(file__isnull=True).count()

    return total_file,miss_file


# 读取上传的excel，并根据内容找出对应的物料或图纸
def appbom_form_upload(app_id,path, include_child):
    rst=read_design_BOM(path,'APPLICATION')
    if 'bom' in rst:
        bom = get_parts_from_bom(rst['bom'], include_child)
        update_app_bom(app_id, bom)
        total_f,miss_f = check_app_file(app_id)

        Application.objects.filter(app_id=app_id).update(total_file=total_f,miss_file=miss_f)
        


def appbom_form_archiveid(app_id, ar_no):
    bom = filefind(type='archive',search=ar_no,opt='AND')

    for item in bom:
        new=ApplicationBom()
        new.app_id=app_id
        new.code=item.get('code','')
        
        new.draw=item.get('filename',"")
        new.name=item.get('name',"")
        if new.code:
            new.part_id =new.code
        new.file_id=item['file_no']
        new.save()


# 查询所申请的图纸列表
def app_bom_find(search):
    files=[]
    qy=ApplicationBom.objects.filter(app_id=search).all()
    for item in qy:
        files.append(item.to_dict())
    
    return files


def app_find(search=None):
    files = []
    qy = Application.objects.all()
    for item in qy:
        files.append(item.to_dict())

    return files
