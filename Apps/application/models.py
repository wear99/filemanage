from django.db import models
#from files.models import ssFile
from django.db.models.deletion import SET_NULL,PROTECT
from django.forms.models import model_to_dict
from django.utils import timezone
import uuid,os

# Create your models here.
# 图纸申请单,需审核,关联流程; 
# 申请图纸库，将申请的物料写入，物料自动关联到图纸; 


def upload_to(instance, filename):
    # 将文件名加上随机字符，避免被直接访问
    name, ext = os.path.splitext(filename)
    t=str(timezone.now().strftime("%Y-%m-%d-%H-%M"))
    filename = '{}{}'.format(t, ext)
    return "PDgroup/Application/{0}/{1}".format(instance.product.product_name, filename)


def create_appno():
    # 从文件库中查询出指定类型的最后一条，返回新的no值
    year = str(timezone.now().year)
    last = Application.objects.filter(app_no__startswith='DA'+year).order_by('app_no').last()

    if last:
        new = int(last.app_no[2:])+1
        new = 'DA'+str(new)
    else:
        new = 'DA'+year+'0001'
    return str(new)


# 图纸申请单
class Application(models.Model):
    app_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app_no = models.CharField(
        max_length=20, default=create_appno, unique=True, verbose_name='申请单号')

    description = models.CharField(max_length=256, verbose_name='申请说明')
    
    product = models.ForeignKey(
        'archive.Product', on_delete=PROTECT, verbose_name='产品名称')    

    file = models.FileField(upload_to=upload_to,
                            max_length=255,null=True, blank=True, verbose_name='申请文件')
    bom = models.FileField(
        upload_to=upload_to, max_length=255, null=True, blank=True, verbose_name='申请文件清单')
    # 0 编辑中，1 审核节点1；2 审核节点2....10 结束
    #status = models.IntegerField(default=0, verbose_name='申请单状态')
    status = models.ForeignKey(
        'process.Process', on_delete=SET_NULL,null=True, verbose_name='审批流程')

    username = models.CharField(max_length=18, verbose_name='申请人')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='申请时间')

    class Meta:
        verbose_name = '图纸申请单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.app_no
    
    def to_dict(self):
        item=model_to_dict(self,exclude=('product','file','bom'))
        item['app_id'] = str(self.app_id)
        item['product'] = self.product.product_name
        item['product_code'] = self.product.product_code
        item['add_time'] = self.add_time.strftime("%Y-%m-%d %H:%M")
        item['status']=self.status.step_name
        if self.bom:
            item['bom']='有'
        return item


# 根据申请单匹配的图纸清单：关联到申请单、物料
class ApplicationBom(models.Model):
    app = models.ForeignKey(
        'Application', on_delete=PROTECT, verbose_name='申请单号')
    
    # 用于记录原始申请信息
    sn = models.CharField(max_length=60, null=True, verbose_name='序号')
    code = models.CharField(max_length=60, null=True, verbose_name='编码')
    draw = models.CharField(max_length=50, null=True, verbose_name='图号')
    name = models.CharField(max_length=50, null=True, verbose_name='名称')

    # 所关联的物料,考虑到有时候没有图纸，所以用物料来记录，便于发现缺少的图纸
    part = models.ForeignKey(
        'parts.PartCode', null=True, on_delete=SET_NULL, verbose_name='物料')

    # 只有当一个图纸没有编码关联时，才记录其图纸号
    file = models.ForeignKey(
        'files.ssFile', null=True, on_delete=SET_NULL, verbose_name='图纸')
    
    is_download=models.IntegerField(default=0,verbose_name='下载')

    class Meta:
        verbose_name = '图纸申请明细'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code
    
    def to_dict(self):
        item=model_to_dict(self,exclude=('app'))
        item['app_id'] = str(self.app_id)
        if self.part and self.part.file:
            file = self.part.file.to_dict()
            item.update(file)
        elif self.file:
            file = self.file.to_dict()
            item.update(file)
        return item



