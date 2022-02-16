from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator

from django.utils import timezone
from .models import Archive

from archive.method import *
from parts.search import get_bom_model
from files.methods import get_ssfile_model

from django.http.response import Http404, HttpResponse, JsonResponse, FileResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, FormView, View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from archive.forms import ArchiveForm
from archive.models import Archive

from django.urls import reverse
from django.db.models import Q
from urllib.parse import quote


# Create your views here.

# 新增发放单，需权限判断

class ArchiveAddView(PermissionRequiredMixin, View):
    permission_required = 'archive.add_archive'
    def get(self,request):
        form=ArchiveForm()
        request.session['has_commented'] = False
        return render(request, 'archivearchive_add.html', locals())
    
    def post(self,request):
        if request.session.get('has_commented', False):
            return HttpResponse("You've already commented.")

        form = ArchiveForm(request.POST, request.FILES)
        if form.is_valid():
            new = form.save(commit=False)
            new.username = self.request.user.username
            new.save()

            request.session['has_commented'] = True

            return redirect(reverse('archive:edit', args=[str(new.archive_id)]))

        return render(request, 'archivearchive_add.html', locals())
        # 传递位置参数用 args；url地址类似：books\1
        # return redirect(reverse('files:archivedetail'), args=[new.archive_id])

        # 传递关键词参数用kwargs;  url地址类似 books?id=1
        # return redirect(reverse('files:archivedetail'), kwargs={'id': new.archive_id})

        # return redirect('files:upload',foo='12345')

# 发放单详情
class ArchiveDetailView(LoginRequiredMixin, View):
    # 先展示发放单，可以进行修改；页面增加 上传文件 按钮，跳转上传文件 
    def get(self,request,pk=None):        
        if pk:
            obj = get_object_or_404(Archive, pk=pk)
            draw_num = get_ssfile_model(
                str(obj.archive_id), 'ARCHIVE_ID').count()

            return render(request, 'archive/archive_detail.html',locals())
        else:
            return redirect('archive:search')

    # 用ajax的方式对编辑按钮权限进行判断
    def post(self,request, pk=None):        
        if pk:
            obj=Archive.objects.get(pk=pk)
            if obj and obj.designer!=self.request.user.username:
                return JsonResponse("'权限不足'", safe=False)
            else:
                #self.request.session['archive'] = str(obj.archive_id)
                return redirect('archive:edit')


# 修改发放单
class ArchiveEditView(PermissionRequiredMixin, View):
    permission_required = 'files.change_archive'    
    def get(self,request,pk=None):        
        obj = get_object_or_404(Archive,pk=pk)
       
        # 对身份进行判断，只有发放人或工艺人员才可以修改
        can_upbom, can_upfile = can_edit_archive(obj, request.user)

        if can_upbom or can_upfile:            
            form=ArchiveForm(instance=obj)            
            return render(request, 'archive/archive_edit.html', locals())
        else:
            title = 'Forbidden'
            info='无此权限进行编辑'
            return render(request, 'info.html', locals())

    def post(self,request,pk=None):
        #pk = self.request.session.get('archive',None)
        ar_id=request.POST.get('archive_id',None)        
        obj=get_object_or_404(Archive,pk=ar_id)
        form = ArchiveForm(request.POST,request.FILES,instance=obj)
        #files = request.FILES.getlist('files')
        if form.is_valid():
            obj = form.save(commit=False)
            obj.username = self.request.user.username
            obj.add_time=timezone.now()
            obj.save()
            return redirect(reverse('archive:detail', args=[ar_id]))
        else:
            return render(request, 'archive/archive_edit.html', locals())        


# 上传BOM视图，需权限判断,bom提交到
class ArchiveBomUploadView(PermissionRequiredMixin, View):
    permission_required = 'archive.add_archive'
    def get(self, request,pk):
        obj=get_object_or_404(Archive,pk=pk)
        return render(request, 'archive/archive_bom_upload.html', locals())        


# 上传文件,增加权限控制,文件提交到files
class ArchiveUploadFileView(PermissionRequiredMixin, View):
    permission_required = 'files.add_ssfile'

    def get(self, request, ar_id):
        obj = get_object_or_404(Archive, pk=ar_id)
        request.session['has_post_file'] = False
        if obj.username != request.user.username:   # 需进行权限判断：只有发放人才可以上传图纸
            return render(request, 'info.html', {'info': '只有发放人才可以上传'})
        
        return render(request, 'archive/archive_file_upload.html', locals())



# 采用Bootstrap table 的get请求
class ArchiveFindView(LoginRequiredMixin, View):
    def get(self, request):
        
        return render(request, 'archive/archive_find_table.html', locals())

    def post(self, request):
        search = request.POST.get('search', None)
        field_type = request.POST.get('field_type', None)
        rows=[]
        if search:
            rows = archivefind(search,field_type)
        total = len(rows)
        return JsonResponse({'total': total, 'rows': rows})



class ArchiveBomListView(ListView):
    template_name = 'archive/archive_bomlist.html'
    context_object_name = 'model_obj'
    paginate_by = 50  # 每页数量

    def get_queryset(self):
        # 获取url中位置参数，要在path里面定义好
        ar_id=self.kwargs['pk']
        if ar_id:
            ar = Archive.objects.get(pk=ar_id)
            queryset = get_bom_model('ARCHIVE',ar_id)
        else:
            queryset=[]
        return queryset

    def get_context_data(self, **kwargs):
        # 拿到原来的方法
        context = super().get_context_data(**kwargs)
        # 然后就可以向模板中添加自定义的一些数据
        ar_id = self.kwargs['pk']
        if ar_id:
            ar = Archive.objects.get(pk=ar_id)
            context['ar_no'] = ar.archive_no
            context['ar_pd'] = ar.product            
        return context


class ArchiveBomView(View):
    def get(self,request,pk):
        if pk:
            obj = get_object_or_404(Archive, pk=pk)
            queryset = get_bom_model('ARCHIVE', pk)
        else:
            queryset = []

        paginator = Paginator(queryset, 25)  # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        title = obj.archive_no + '-'+ obj.product.product_name +'-'+obj.get_stage_display()
        
        if obj.stage==100:
            return render(request, 'archive/archive_changebom.html', locals())
        else:
            return render(request, 'archive/archive_bom.html', locals())



class ArchiveFileListView(ListView):
    template_name = 'archive/archive_filelist.html'
    context_object_name = 'model_obj'
    paginate_by = 50  # 每页数量

    def get_queryset(self):
        # 获取url中位置参数
        ar = self.kwargs['pk']
        if ar:
            queryset =  get_ssfile_model(ar,'ARCHIVE_ID')
        else:
            queryset = []
        return queryset

    def get_context_data(self, **kwargs):
        # 拿到原来的方法
        context = super().get_context_data(**kwargs)
        # 然后就可以向模板中添加自定义的一些数据
        ar = self.kwargs['pk']
        if ar:
            ar = Archive.objects.get(pk=ar)
            context['ar_no'] = ar.archive_no
            context['ar_pd'] = ar.product
        return context



def DownloadBom(request, pk):    
    obj=get_object_or_404(Archive,archive_id=pk)
    if not obj.bom:
        return HttpResponse(status=204)

    response = FileResponse(obj.bom.open(mode='rb'))
    response['content_type'] = "application/octet-stream"

    # 指定文件以附件形式下载，否则会直接在浏览器打开
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        quote(obj.name))
    return response


