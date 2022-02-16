from django.shortcuts import render
from .models import ProcessLog
# Create your views here.


def AddTasklog(task_id,process,username=None, rst=1, rmk=None):
    # 审批记录
    log = ProcessLog()
    log.task_id = task_id
    log.type = process.name
    log.step = process.step
    log.step_name = process.step_name
    log.username =  process.username or username
    log.result = rst
    log.remark = rmk
    log.save()
