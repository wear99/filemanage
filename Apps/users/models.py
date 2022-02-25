from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib import auth
# Create your models here.

# 定义用户模型，添加额外的字段
# 需要在settings中指定自定义认证模型：AUTH_USER_MODEL = 'users.UserProfile'
class UserProfile(AbstractUser):
    
    ch_name = models.CharField(max_length=8, default='姓名',verbose_name="姓名")
    role = models.CharField(max_length=20,default='员工',verbose_name="角色")
    phone = models.CharField(max_length=15, blank=True, verbose_name="电话")
    department = models.CharField(max_length=15, verbose_name="部门")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
# 角色模型
class Role(models.Model):
    role = models.CharField(max_length=12, verbose_name="角色")
    permission = models.IntegerField(default=1, verbose_name="权限")

    class Meta:
        verbose_name = '角色信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.role

# 用户操作记录    
class UserLog(models.Model):
    username = models.CharField(max_length=20, verbose_name="用户名")
    type = models.CharField(max_length=20, verbose_name="操作类型")
    remark=models.CharField(max_length=120,verbose_name="备注")
    add_time = models.DateTimeField(
        default=timezone.now, verbose_name='操作时间')

    class Meta:
        verbose_name = '操作记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.type
