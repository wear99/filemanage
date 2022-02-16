from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse, FileResponse
from django.views.generic import View
from tools.check_excel import *
from files.views import download_from_path
from filemanage.settings import BASE_DIR 
from django.utils import timezone
import os,json,time
# Create your views here.


def Get_task_status(request,task_id):
    if task_id in task_status:
        return JsonResponse(task_status[task_id],safe=False)


class CheckCodeView(View):  # 检查excel中编码: 先将文件保存，然后读取，检查并更新后，再返回下载
    #permission_required = 'partcode.add_archive'
    def get(self, request):
        task_id = str(time.time())
        
        return render(request, 'tools/check_code.html', locals())

    def post(self, request):
        f = request.FILES.get('file', None)
        task_id=request.POST.get('task_id')
        task_status[task_id] = []
        if not f:
            return
        ext = os.path.splitext(f.name)[-1]
        if ext.upper() != '.XLSX':
            title = '文件格式不对'
            return render(request, 'info.html', locals())

        #将文件保存在temp
        fpath = os.path.join(BASE_DIR, 'sstech/temp/checkcode/'+f.name)
        with open(fpath, 'wb+') as d:
            for chunk in f.chunks():
                d.write(chunk)

        task_status[task_id].append({'task':'上传文件','rst':'完成'})
        rst = check_excel_code(fpath,task_id)
        if 'error' in rst:
            title = '出错了'
            info = rst['error']
            return render(request, 'info.html', locals())

        # 返回下载
        
        res=download_from_path(fpath)
        task_status[task_id].append({'task': '处理完毕', 'rst': ''})
        return res
