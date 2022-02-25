# 处理方法
from .models import ssFile,get_ssfile_model

from django.utils import timezone
from django.db.models import Q
import os,zipfile,zipstream
import threading

from parts.loadpart import  all_code
from parts.update import part_file
from parts.search import Partfind_dict, childfind_current
from files.pdfhander import files_add_mark


# 把已存在的同名文件、同发放类型的,按日期排序,只保留最新的，其余设为 失效0；
def check_file_valid(obj):
    ex = ssFile.objects.filter(filename=obj.filename, stage=obj.stage,file_valid=1).exclude(
        file_id=obj.file_id).order_by('add_time').last()
    if ex:  #比较时间
        if obj.add_time < ex.add_time:
            obj.file_valid = 0
            obj.valid_info = ex.file_id
            obj.valid_time = ex.add_time
            obj.save()

        else:
            ex.file_valid = 0
            ex.valid_info = obj.file_id
            ex.valid_time = obj.add_time
            ex.save()

    # 如果是小批，还应把试制图纸设为失效
    if obj.stage.stage_id==9:
        ssFile.objects.filter(filename=obj.filename,
                                stage=5, file_valid=1).update(file_valid=0, valid_info=obj.file_id, valid_time=obj.add_time)


# 上传文件处理：写入数据库；同图号的设为失效；加水印；和物料进行关联；
def upload_file(ar_obj, files):
    add_mark = []
    up_files = {}
    for f in files:
        fname, ext = os.path.splitext(f.name.upper())   # 要去掉扩展名

        new=ssFile()
        new.filename=fname
        new.archive = str(ar_obj.archive_id)
        new.stage = ar_obj.stage
        new.product = ar_obj.product
        new.username = ar_obj.username
        new.filepath=f
        new.add_time = ar_obj.add_time
        new.save()


        if ext == '.PDF':  # 增加文件水印
            add_mark.append(
                {
                    'filepath': new.filepath.path,
                    'stage': new.stage.stage_name,
                    'file_id': new.file_id,
                    'add_time': new.add_time
                }
                )
            up_files[new.file_id] = new

        # 写入上传记录
        #LogFile(new, 'Upload', username)

    # 将同名文件设置为失效
    for obj in up_files.values():
        check_file_valid(obj)

    # 进行文件和物料的关联
    part_file(ar_obj.archive_id, bom=None, filelist=up_files.keys())

    # 后台写入水印
    threading.Thread(target=files_add_mark, args=[add_mark]).start()

    return up_files


# 查找文件
def filefind(search,field_type):
    objs = get_ssfile_model(search, field_type)
    files = []
    for item in objs.values():
        item['add_time'] = item['add_time'].strftime("%Y-%m-%d")

        # 查找图纸被关联的物料
        for key,value in all_code.items():
            if value['file_id']==item['file_id']:
                #part = obj.partcode_set.last()
                item['code'] = value['code']
                item['name'] = value['name']
                item['draw'] = value['draw']

        files.append(item)

    return files


def childfind_file(fileid):
    '利用当前设计bom表，查找该文件的子图纸'
    #先找到该文件的物料号
    fcode=Partfind_dict(fileid,'file_id')

    if not fcode:
        return
    fcode=fcode[-1]['code']

    #用编码去查找子零件bom
    fbom=childfind_current(fcode,)
    if not fbom:
        return

    id=[]
    for item in fbom:
        id.append(item['file_id'])

    files = filefind(id,'FILE_ID')

    return files


#多文件打包为zip
class ZipFiles_class():
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(
            mode='w', compression=zipstream.ZIP_DEFLATED)

    def toZip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=name)
        else:
            self.addFolderToZip(file, name)

    def addFolderToZip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(full_path, arcname=os.path.join(
                    name, os.path.basename(full_path)))
            elif os.path.isdir(full_path):
                self.addFolderToZip(full_path, os.path.join(
                    name, os.path.basename(full_path)))

    def close(self):
        if self.zip_file:
            self.zip_file.close()


def ZipFile_objs(file_objs):
    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
    for obj in file_objs:
        name, ext = os.path.splitext(obj.filepath.path)
        z.write(obj.filepath.path, arcname=obj.filename+ext)
    return z
