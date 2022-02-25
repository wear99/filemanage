from files.models import ssFile
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from .forms import ApplicationForm,ApprovalForm, ProvidForm
from .models import Application
from .methods import *
from files.views import DownloadFile_zip
from process.models import Process,ProcessLog
from process.views import AddTasklog
from django.views.generic import ListView, DetailView, FormView, View
from datetime import date,datetime
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from parts.forms import PartFindForm
import json
# Create your views here.

# 申请图纸，上传物料清单，自动对应的图纸，包含子件图纸；不再手工提交、发放图纸。
# 清单字段：编码，图号，名称，文件号，


def GetProvidlist(appno):
    obj=Application.objects.filter(appno=appno).last()
    if obj and obj.providlist:
        return eval(obj.providlist)
    else:
        return []


# 新增申请单，需权限判断
# 申请bom在线填写？上传excel？

class AppAddView(LoginRequiredMixin,View):
    def get(self,request):
        form = ApplicationForm()
        request.session['has_commented'] = False
        return render(request, 'application/app_add.html', locals())
    
    def post(self, request):
        # 检查是否重复提交
        if request.session.get('has_commented', False):
            return HttpResponse("You've already commented.")
            
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            new = form.save(commit=False)            
            new.username = self.request.user.username
            new.status=Process.getNew('图纸申请流程')
            new.save()

            request.session['has_commented'] = True

            #bom_file = request.FILES.get('bom')
            ar_no = form.cleaned_data.get('archive_no', None)
            include = form.cleaned_data.get('include',True)

            if new.bom:
                appbom_form_upload(new.app_id,new.bom.path,include)
            elif ar_no:
                appbom_form_archiveid(new.app_id,ar_no)

            # 新增提交记录
            AddTasklog(new.app_no,new.status,new.username)

            # 进入下一个审批节点
            new.status=new.status.NextStep()
            new.save()
            if new.status.step==10:
                # 申请单结束，无需审批时插入记录                 
                AddTasklog(new.app_no, new.status, new.username)

            return redirect('application:list')


# 申请单列表,obj形式
class AppListView_obj(LoginRequiredMixin,ListView):
    model = Application
    template_name = 'application/app_list_obj.html'
    context_object_name = 'model_obj'
    paginate_by = 10  # 每页数量

    def get_queryset(self):
        queryset = Application.objects.all().order_by()
        # 获取url中位置参数
        #st = self.kwargs['status']
        st=self.kwargs.get('status',None)
        if st=='my':
            queryset = queryset.filter(Q(username=self.request.user.username) | Q(
                status__username=self.request.user.username))
        elif st == 'pending':            
            queryset = queryset.exclude(status__step=10)
        elif st == 'closed':            
            queryset = queryset.filter(status__step=10)

        return queryset


# 申请单列表,get时返回模板及全部申请的json文件；post时可以带参数查找
class AppListView(LoginRequiredMixin, View):
    def get(self, request):
        rows=json.dumps(app_find())
        return render(request, 'application/app_list_find_table.html', locals())

    def post(self, request):
        search = request.POST.get('search', None)
        type = request.POST.get('tp', None)
        rows = app_find(search)        
        total = len(rows)
        return JsonResponse({'total': total, 'rows': rows})


# 申请单详情
class AppDetailView(View):
    def get(self, request, pk):        
        appobj=get_object_or_404(Application,app_id=pk)

        # 审批记录
        #task = ProcessLog.objects.filter(appno=appobj.appno).order_by()

        # 申请图纸列表        
        app_items = json.dumps(app_bom_find(pk))
        return render(request, 'application/app_detail.html', locals())


# 根据pk展示申请单; 当人员具有权限时，显示对应的审批信息
class ApprovalView(LoginRequiredMixin,View):
    def get(self, request, pk):
        # pk是申请单
        appobj = get_object_or_404(Application, app_id=pk)
        # 审批记录
        task = ProcessLog.objects.filter(appno=pk).order_by()       
        return render(request, 'application/app_approval.html', locals())
    
    def post(self, request, pk):
        form = ApprovalForm(request.POST)        
        if form.is_valid():                       
            res = form.cleaned_data.get('result')
            rmk = form.cleaned_data.get('remark')
            app_id = form.cleaned_data.get('app_id')
            
            obj = get_object_or_404(Application,app_id=app_id)

            if request.user.username!=obj.status.username: #再次对用户进行判断
                return redirect('application:list')

            # 写入Log
            AddTasklog(obj.appno, obj.status, obj.username,res,rmk)
            

            if res:
                # 审批通过,创建下一任务
                obj.status = obj.status.NextStep()
            else:
                # 审批不通过，退回重新编辑
                obj.status=obj.status.Backup()                
            obj.save()

            if obj.status.step == 10:  #申请单结束，插入记录
                AddTasklog(obj.appno, obj.status, obj.username)                

            return redirect('application:list')
        else:
            return render(request, 'application/app_approval.html', locals())


# 向申请单添加图纸,页面分2块，一个是添加的图纸表，一个是图纸查询
class ProvidfileView(View):
    def get(self, request, pk):
        # pk是申请单
        obj = get_object_or_404(Application, appno=pk)
        appfile = eval(obj.filelist)
        form = PartFindForm()
        if obj.providlist:
            filelist=eval(obj.providlist)
            fileobj = ssFile.objects.filter(file_id__in=filelist)
        return render(request, 'application/provid.html', locals())
    
    def post(self, request, pk):
        # ajax形式提交
        # 接收文件的id列表，存入申请的providlist中        
        form=ProvidForm(request.POST)
        if form.is_valid():            
            app_no = form.cleaned_data.get('appno')
            obj = get_object_or_404(Application, appno=app_no)

            obj.providlist = form.cleaned_data['providlist']
            obj.provid_user=self.request.user.username
            obj.provid_time=datetime.today()
            obj.save()
            return JsonResponse({'msg':'已保存'})
        return JsonResponse({'msg': '有错误'})


# 文件下载，要经过权限判断，不能直接暴露在url中
def App_file_download(request):
    file_ids = request.POST.get('download_files', [])
    file_ids = json.loads(file_ids)

    app_id = request.POST.get('app_id',None)
    appobj = get_object_or_404(Application, app_id=app_id)

    # 权限判断:只有申请单本人可以下载
    if appobj.username==request.user.username:
        DownloadFile_zip(file_ids, request.user.username)
    else:
        title = '只有申请人可以下载'
        info = ''
        return render(request, 'info.html', locals())






        

