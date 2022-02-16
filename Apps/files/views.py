from django.http import request, FileResponse, JsonResponse, StreamingHttpResponse, Http404
from django.shortcuts import redirect, render,get_object_or_404
from django.views.generic import ListView, DetailView, FormView, View

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required,permission_required
from files.forms import FileFindForm
from files.methods import *
from urllib.parse import quote

from archive.views import get_archive_model

import base64


# Create your views here.

# 流程：先建立发放单，然后再上传图纸；或从发放列表选择自己的，再上传图纸；
# 对于直接输入url文件地址的，只能把文件名+uuid 复杂化

# 上传文件,增加权限控制
class FileUploadView_archive(PermissionRequiredMixin, View):
    permission_required = 'files.add_ssfile'
    def post(self, request):

        if request.session.get('has_post_file', False):
            return 

        ar_id = request.POST.get('archive_id',None)
        files = request.FILES.getlist('files')  

        obj = get_archive_model(ar_id, 'archive_id')

        if not obj:
            return Http404        
        request.session['has_post_file'] = True

        rst = upload_file(obj, files, request.user.username)  # 上传文件处理        

        i = '文件上传成功'
        return render(request, 'info.html', {'info': i})


# 具有分页，使用listview
class FindFileView(ListView):
    model = ssFile
    template_name = 'files/filefind.html'
    context_object_name = 'model_obj'
    paginate_by = 50  # 每页数量 
    
    def get_queryset(self):
        form = FileFindForm(self.request.GET)
        search=form.data.get('search',None)
        type = form.data.get('fd', None)
        opt = form.cleaned_data.get('opt',None)
        if search:
            search = search.split(" ")
        else:
            search=[]
        queryset = filefind(type, search,opt)        

        return queryset

    def get_context_data(self, **kwargs):
        # 拿到原来的方法
        context = super().get_context_data(**kwargs)
        # 然后就可以向模板中添加自定义的一些数据
        form = FileFindForm(self.request.GET)
        context['form']=form
        return context


# 用bootstrap-table
class FileFindView_table(View):
    def get(self, request):

        return render(request, 'files/file_find_table.html', locals())

    def post(self, request):    #当filefind页面查找时，用post方法，这时候只返回数据       
        search = request.POST.get('search', None)
        field_type = request.POST.get('field_type', None)
        
        files = []
        if search:
            #search = search.split(" ")
            files = filefind(search,field_type)

        total = len(files)            
        return JsonResponse({'total': total, 'rows': files})


# 权限控制
@permission_required('files.view_ssfile')
def ViewFile(request,file_id):
    # 需要对文件做验证，例如后缀名、该用户是否有权限等
    # 或者对文件名加uuid，让对方没办法猜出名字来输地址
    obj = get_object_or_404(ssFile, file_id=file_id)

    # 记录log
    LogFile(obj, 'View',request.user.username)

    # 返回一个文件的base64编码
    f = obj.filepath.open(mode='rb')
    b64 = base64.b64encode(f.read())
    return render(request, 'files/fileview_pdfjs.html', {"b64": str(b64, 'utf-8')})
    '''
    if type=="open2":
        # 直接用浏览器打开
        response = FileResponse(obj.file.open(mode='rb'))            
        response['content_type'] = "application/octet-stream" 
        return response

    '''


@permission_required('files.download_ssfile')
def DownloadFile(request, file_id):
    obj = get_object_or_404(ssFile,file_id=file_id)
    LogFile(obj, 'Download', request.user.username)
    response = FileResponse(obj.filepath.open(mode='rb'))
    response['content_type'] = "application/octet-stream"
    
    # 指定文件以附件形式下载，否则会直接在浏览器打开
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        quote(obj.filename))
    return response


# 多文件下载，采用form提交，打包为zip文件下载:
# ajax无法保存文件，所以把文件号放在form里

def DownloadFile_zip(file_ids,username):

    file_objs = ssFile.objects.filter(file_id__in=file_ids)
    z=ZipFiles_class()
    for obj in file_objs:
        name, ext = os.path.splitext(obj.filepath.path)
        z.toZip(obj.filepath.path, obj.filename+ext)

        LogFile(obj, 'app_download', username)

    name = str(timezone.now().strftime("%Y*%m-%d-%H-%M"))+'.zip'

    response = StreamingHttpResponse(
        z.zip_file, content_type='application/zip')
    response['content_type'] = "application/octet-stream"    
    response['Content-Disposition'] = 'attachment;filename={0}'.format(quote(name))
    return response


def download_from_path(fpath):    
    response = FileResponse(open(fpath, 'rb'))    
    response['content_type'] = "application/octet-stream"
    # 指定文件以附件形式下载，否则会直接在浏览器打开
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        quote(os.path.basename(fpath)))

    return response



