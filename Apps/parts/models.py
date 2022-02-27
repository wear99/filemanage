from django.db import models
from django.utils import timezone
from django.db.models.deletion import SET_NULL, PROTECT
from django.forms.models import model_to_dict

# Create your models here.


# 编码唯一；没编码的用图号+名称
class PartCode(models.Model):
    code = models.CharField(max_length=60, unique=True,
                            primary_key=True, verbose_name='编码')
    draw = models.CharField(max_length=50, blank=True,
                            null=True, verbose_name='图号')
    name = models.CharField(max_length=50, verbose_name='名称')
    material = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='材料')
    weight = models.FloatField(
        max_length=6, blank=True, null=True, verbose_name='重量')
    remark = models.CharField(
        max_length=20, blank=True, null=True, verbose_name='备注')
    division = models.CharField(
        max_length=20, blank=True, null=True, verbose_name='分工')

    part_valid = models.IntegerField(default=1, verbose_name='状态')
    valid_time = models.DateTimeField(null=True, verbose_name='失效时间')

    add_time = models.DateTimeField(default=timezone.now,blank=True, null=True, verbose_name='时间')
    file = models.ForeignKey(
        'files.ssFile', on_delete=SET_NULL, null=True, verbose_name='图纸')

    class Meta:
        verbose_name = '物料库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code

    def to_dict(self):
        item=model_to_dict(self)
        item['add_time'] = self.add_time.strftime("%Y-%m-%d %H:%M")



class PartCost(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=60,null=True,verbose_name='编码')
    material_cost = models.FloatField(max_length=8, default=0, verbose_name='材料成本')
    labor_cost = models.FloatField(
        max_length=8, default=0, verbose_name='人工成本')
    managed_cost = models.FloatField(
        max_length=8, default=0, verbose_name='管理成本')
    cost = models.FloatField(max_length=8, default=0, verbose_name='单件成本')

    source = models.CharField(max_length=20, default='导入', verbose_name='成本来源')
    cost_valid = models.IntegerField(default=1, verbose_name='状态')
    valid_time = models.DateTimeField(null=True, verbose_name='失效时间')

    add_time = models.DateTimeField(default=timezone.now, verbose_name='时间')

    class Meta:
        verbose_name = '成本库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code


# 发放清单---设计BOM
# 结构：发放单号, 序号，子项，数量，备注
class ArchiveBom(models.Model):
    id = models.AutoField(primary_key=True)
    sn = models.CharField(max_length=32, verbose_name='序列号')

    archive = models.CharField(max_length=64, null=True, verbose_name='发放单号')

    #生成最新Bom时判断有效性问题：小批最高10，试制5，实验1，
    stage = models.ForeignKey('archive.StageType',
                              on_delete=PROTECT,
                              verbose_name='发放类型')

    parent = models.CharField(max_length=32, null=True, verbose_name='父项编码')
    child = models.ForeignKey(
        'PartCode', on_delete=PROTECT, verbose_name='子件编码')
    quantity = models.FloatField(max_length=4, verbose_name='数量')

    bom_valid = models.IntegerField(default=1, verbose_name='Bom状态')
    valid_info = models.CharField(max_length=128,null=True,verbose_name='失效单号')
    valid_time = models.DateTimeField(null=True,verbose_name='失效时间')

    remark = models.CharField(max_length=50, null=True, verbose_name='备注')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='更新时间')

    class Meta:
        verbose_name = '物料发放BOM'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sn+self.parent

    def to_dict(self):  # 物料序列化
        item = model_to_dict(self, exclude=('child'))
        #item['archive'] = self.archive.archive_no
        #item['archive_id'] = str(self.archive.archive_id)

        item['sort_key'] = item['sn'].split('.')[-1]
        child = model_to_dict(self.child, exclude=('add_time'))
        item.update(child)
        item['add_time'] = self.add_time.strftime("%Y-%m-%d")

        return item



# 图纸层级表，主要是为了确定图纸的父子关系，并不是生产所用。所以按设计BOM为准，ERP BOM缺少子件信息。
class CurrentBom(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.CharField(max_length=32, null=True, verbose_name='父项编码')
    child = models.ForeignKey(
        'PartCode', on_delete=PROTECT,null=True ,verbose_name='子件编码', related_name='child')
    quantity = models.FloatField(max_length=4, verbose_name='数量')

    sort_key = models.IntegerField(null=True, verbose_name='排序号')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='更新时间')

    class Meta:
        verbose_name = '当前BOM'
        unique_together = ("parent", "child")
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.parent

    def to_dict(self):  # 物料序列化
        item=model_to_dict(self.child)

        item['id'] = self.id
        item['parent'] = self.parent
        item['quantity'] = self.quantity
        item['add_time'] = self.add_time.strftime("%Y-%m-%d")

        return item


#导入的erp Bom,为了保存不同阶段的信息，所以结构同ArchiveBom,其中archive代表该bom的 产品代码+日期,用于区分不同的导入
class ErpBom(models.Model):
    id = models.AutoField(primary_key=True)
    sn = models.CharField(max_length=32, verbose_name='序列号')

    archive = models.CharField(max_length=64, verbose_name='产品代码')

    stage = models.ForeignKey('archive.StageType',
                              on_delete=PROTECT,
                              verbose_name='发放类型')
    parent = models.CharField(max_length=64, verbose_name='父项编码')
    child = models.ForeignKey(
        'PartCode', on_delete=PROTECT, verbose_name='子件编码')
    quantity = models.FloatField(max_length=4, verbose_name='数量')

    bom_valid = models.IntegerField(default=1, verbose_name='Bom状态')
    valid_info = models.CharField(max_length=128,null=True,verbose_name='失效单号')
    valid_time = models.DateTimeField(null=True, verbose_name='失效时间')

    remark = models.CharField(max_length=50, null=True, verbose_name='备注')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='更新时间')

    class Meta:
        verbose_name = '导入的ERP-BOM'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sn+self.parent

    def to_dict(self):  # 物料序列化
        item = model_to_dict(self, exclude=('child',))

        item['sort_key'] = item['sn'].split('.')[-1]
        child = model_to_dict(self.child, exclude=('add_time'))
        item.update(child)
        item['add_time'] = self.add_time.strftime("%Y-%m-%d")

        return item


# 设计更改Bom
class Change(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.CharField(max_length=32, null=True, verbose_name='父项编码')
    archive = models.CharField(max_length=64, null=True, verbose_name='发放单号')

    sn = models.CharField(max_length=32, verbose_name='序号')
    draw = models.CharField(max_length=50, null=True, verbose_name='图号')
    name = models.CharField(max_length=50, verbose_name='名称')
    before_code = models.CharField(max_length=60, null=True, verbose_name='更改前编码')
    after_code = models.CharField(
        max_length=60, null=True, verbose_name='更改后编码')
    before_description = models.CharField(
        max_length=60, null=True, verbose_name='更改前说明')
    after_description = models.CharField(
        max_length=60, null=True, verbose_name='更改后说明')
    change_type = models.IntegerField(default=2, verbose_name='更改类别')
    change_draw = models.CharField(
        max_length=20, null=True, verbose_name='更改方式')
    stock = models.IntegerField(null=True, verbose_name='库存')
    on_order = models.IntegerField(null=True, verbose_name='在制')
    suggestion = models.CharField(
        max_length=50, null=True, verbose_name='处理建议')
    product = models.CharField(
        max_length=50, null=True, verbose_name='涉及产品')

    add_time = models.DateTimeField(default=timezone.now, verbose_name='更新时间')

    class Meta:
        verbose_name = '设计更改清单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sn+self.parent
