from django.db import models
from django.db.models.deletion import SET_NULL,PROTECT
from django.forms.models import model_to_dict
from datetime import datetime
from uuid import uuid4
import os
from django.utils import timezone
from filemanage.settings import stage_type
# Create your models here.
# 检查并创建迁移项
# python manage.py makemigrations

# 执行迁移命令
# python manage.py migrate
# 生成文档编码


def createfileno():
    # 从文件库中查询出指定类型的最后一条，返回新的no值
    year = timezone.now().year-2000
    last = ssFile.objects.filter(file_id__startswith=year).last()
    #print(lastno)
    if last:
        new = last.fileno+1
    else:
        new = year*10000+1
    return new


def upload_to(instance, filename):
    # 将文件名加上随机字符，避免被直接访问
    name, ext = os.path.splitext(filename)
    filename = '{}_{}{}'.format(name,uuid4().hex[:10], ext)

    return "PDgroup/{0}/{1}/{2}".format(instance.product.product_name, instance.stage.stage_name, filename)


class ssFile(models.Model):
    file_id = models.IntegerField(
        default=createfileno, verbose_name='文件编号', unique=True, primary_key=True)
    filename = models.CharField(max_length=64, verbose_name='图号')

    # 图纸的阶段标记,试制S,小批A,定制C,实验Y,一次性O
    # get_stage_display()   取出选项对应的字段

    stage = models.ForeignKey(
        'archive.StageType', on_delete=PROTECT, verbose_name='发放类型')

    product = models.ForeignKey(
        'archive.Product', on_delete=PROTECT, verbose_name='产品名称')

    archive = models.CharField(max_length=64, null=True, verbose_name='发放单号')
    
    # 应和权限结合起来？一张图纸可能会对应多个部门
    output = models.CharField(
        max_length=20, blank=True, null=True, verbose_name='发放部门')

    # 图纸是否有效
    file_valid = models.IntegerField(default=1, verbose_name='图纸状态')
    valid_info = models.CharField(
        max_length=128, blank=True, null=True, verbose_name='状态说明')
    valid_time = models.DateTimeField(blank=True, null=True, verbose_name='失效时间')

    #图纸对应物料(仅图纸发放时记录，如果编码更新了不会记录)
    original_code = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='原始物料')

    # 图纸所属用户
    username = models.CharField(max_length=30, verbose_name='设计')
    
    # 图纸文件
    filepath = models.FileField(upload_to=upload_to,
                            max_length=255, verbose_name='文件位置')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='发放时间')

    class Meta:
        verbose_name = '文件'
        verbose_name_plural = verbose_name
        permissions = (('download_ssfile', '可以下载文件'),)

    def __str__(self):
        return self.filename
    
    def to_dict(self):
        item = model_to_dict(self, exclude=('filepath', 'valid_time', 'add_time','stage','product'))       
        item['stage'] = self.stage.stage_name
        item['stage_lv'] = self.stage.stage_lv
        item['product'] = self.product.product_name
        item['product_code'] = self.product.product_code
        item['add_time'] = self.add_time.strftime("%Y-%m-%d %H:%M")
        if self.valid_time:
            item['valid_time'] = self.valid_time.strftime("%Y-%m-%d %H:%M")

        return item

# 下载/查看文件记录
class Filelog(models.Model):
    file_id = models.CharField(max_length=12, verbose_name='文件编号')
    filename = models.CharField(max_length=30,blank=True, verbose_name='文件名称')
    type = models.CharField(max_length=8, default='下载', verbose_name='操作类型')
    username = models.CharField(max_length=30, verbose_name='操作用户')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='操作时间')

    class Meta:
        verbose_name = '文档操作记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.type


def get_ssfile_model(search, type):
    '当search为列表时用In查询，否则用包含查询'

    q = ssFile.objects.all()
    if isinstance(search, list):
        if type == 'DRAW':
            q = q.filter(filename__in=search)
        elif type == 'ARCHIVE_ID':
            q = q.filter(archive__in=search)
        elif type == 'FILE_ID':
            q = q.filter(file_id__in=search)
    else:
        if type == 'DRAW':
            q = q.filter(filename__icontains=search)
        elif type == 'PRODUCT':
            q = q.filter(product__icontains=search)
        elif type == 'USERNAME':
            q = q.filter(username=search)
        elif type == 'ARCHIVE_ID':
            q = q.filter(archive=search)
        else:
            return []

    return q


def LogFile(obj, tp, username):
    # 记录log
    new = Filelog(file_id=obj.file_id, filename=obj.filename,
                  username=username)
    new.type = tp
    new.save()
