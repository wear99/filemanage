from django.db import models
from django.utils import timezone
# Create your models here.

# 审批流程表
class Process(models.Model):
    name = models.CharField(max_length=18, verbose_name='审批流程名')
    step = models.IntegerField(verbose_name='节点序号')
    step_name = models.CharField(max_length=18, verbose_name='节点名称')
    username = models.CharField(
        max_length=18, verbose_name='审批人', blank=True, null=True)

    class Meta:
        verbose_name = '审批流程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name+'-'+self.step_name

    def NextStep(self):
        # 根据当前流程返回下一个流程节点，如果没有则返回10
        name = self.name
        newstep = self.step+1

        new = Process.objects.filter(
            name=name, step=newstep).last()

        if not new:
            # 查找不存在就创建一个,返回元组，第一个是对象，第二个是true或false
            new = Process.objects.get_or_create(
                name=name, step=10, defaults={'step_name': '结束'})[0]
        return new

    def Backup(self):
        new = Process.objects.get_or_create(
            name=self.name, step=0, defaults={'step_name': '提交'})[0]
        return new

    @staticmethod
    def getNew(name):
        new = Process.objects.get_or_create(
            name=name, step=0, defaults={'step_name': '提交'})[0]

        return new

# 审批任务表
class ProcessLog(models.Model):
    #appno = models.ForeignKey('Application',on_delete=SET_NULL,null=True,verbose_name='表单')
    # 不用外键，便于添加多个不同类型表单
    task_id = models.CharField(max_length=32, verbose_name='表单ID')
    type = models.CharField(max_length=18, verbose_name='表单类型')

    step = models.IntegerField(verbose_name='节点序号')
    step_name = models.CharField(max_length=18, verbose_name='节点名称')
    username = models.CharField(max_length=18, verbose_name='审批人')
    result = models.IntegerField(default=1, verbose_name='审核结果')
    remark = models.CharField(
        max_length=64, verbose_name='审核备注', blank=True, null=True)

    add_time = models.DateTimeField(
        default=timezone.now, verbose_name='审核时间', null=True)

    class Meta:
        verbose_name = '审批记录表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.appno+'-'+self.type+'-'+self.step

