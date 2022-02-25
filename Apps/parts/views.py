
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.http.response import Http404, HttpResponse, JsonResponse, FileResponse
from django.views.generic import View
from parts.change import change_child, change_find, change_parent, import_changes

from parts.update import import_upload_parts, import_upload_erpbom, import_archivebom
from parts.forms import FileUploadForm, ArchiveBomUploadForm
from parts.search import *
from parts.cost import bom_add_cost, bom_recalc_cost, import_upload_cost, find_cost_history

from archive.views import get_archive_model

from filemanage.settings import BASE_DIR
import os
import json
# Create your views here.

# ===================================导入 相关视图=========================
# 文件导入统一入口


def uploadFileView(request):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        f = form.cleaned_data['file']
        filetype = form.cleaned_data['filetype']
        add_time = form.cleaned_data['add_time']

        ext = os.path.splitext(f.name)[-1]
        if ext.upper() != '.XLSX':
            title = '文件格式不对'
            return render(request, 'info.html', locals())

        # 将文件保存在temp
        fpath = os.path.join(BASE_DIR, 'sstech/temp/'+f.name)
        with open(fpath, 'wb+') as d:
            for chunk in f.chunks():
                d.write(chunk)

        if filetype == 'part':
            rst = import_upload_parts(fpath, add_time)

        elif filetype == 'cost':
            rst = import_upload_cost(fpath, add_time)

        elif filetype == 'erpbom':
            rst = import_upload_erpbom(fpath, add_time)

        # 统一返回格式：error代表错误, bom 代表返回的结果列表
        if 'error' in rst:
            title = '导入失败'
            info = rst['error']
        else:
            title = '导入成功'
        #table_data = rst['update']

        return render(request, 'info.html', locals())


def save_upload(request):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        f = form.cleaned_data['file']
        filetype = form.cleaned_data['filetype']
        add_time = form.cleaned_data['add_time']

        ext = os.path.splitext(f.name)[-1]
        if ext.upper() != '.XLSX':
            title = '文件格式不对'
            return render(request, 'info.html', locals())

        # 将文件保存在temp
        fpath = os.path.join(BASE_DIR, 'sstech/temp/'+f.name)
        with open(fpath, 'wb+') as d:
            for chunk in f.chunks():
                d.write(chunk)

    return fpath, add_time


class UploadArchivebomView(View):
    def post(self, request, pk):
        form = ArchiveBomUploadForm(request.POST, request.FILES)
        files = request.FILES.get('bom')
        if form.is_valid():
            ar_id = form.cleaned_data.get('archive_id', None)
            obj = get_archive_model(ar_id, 'archive_id')

            if not obj:
                return Http404

            obj.bom = files
            obj.save()

            if obj.get_stage_display() == '设计更改':
                rst = import_changes(obj.bom.path, obj, obj.add_time)
            else:
                rst = import_archivebom(obj.bom.path, obj, obj.add_time)

            if 'error' in rst:
                title = '错误'
                info = rst['error']
                return render(request, 'info.html', locals())
            else:
                return redirect(reverse('archive:bomview', args=[ar_id]))

        return render(request, 'archive/archive_bom_upload.html', locals())


# 上传code表
class UploadPartView(View):
    #permission_required = 'partcode.add_archive'
    def get(self, request):
        filetype = 'part'
        title = '物料库导入'
        col = ('编码', '图号', '名称', '日期')
        return render(request, 'parts/part_upload.html', locals())

    def post(self, request):
        fpath, add_time = save_upload(request)
        rst = import_upload_parts(fpath, add_time)

        if 'error' in rst:
            title = '导入失败'
            info = rst['error']
        else:
            title = '导入成功'
            table_data = rst['update']

        return render(request, 'info.html', locals())


# 上传成本表
class UploadCostView(View):  # 读取上传的成本表，并更新成本库
    def get(self, request):
        filetype = 'cost'
        title = '成本表导入'
        col = ('编码', '名称', '材料成本', '人工成本', '管理成本')
        return render(request, 'parts/part_upload.html', locals())

    def post(self, request):
        fpath, add_time = save_upload(request)
        rst = import_upload_cost(fpath, add_time)

        if 'error' in rst:
            title = '导入失败'
            info = rst['error']
        elif 'ok' in rst:
            title = '导入成功'
            info = "成本更新成功,共读取{0}项,其中新的：{1},变更的成本：{2}".format(
                rst['total'], rst['new'], rst['change'])
            table_data = rst['data']
        return render(request, 'info.html', locals())


# 上传erpbom
class UploadErpBomView(View):
    def get(self, request):
        filetype = 'erpbom'
        title = 'ERP-Bom 导入'
        col = ('层次', '编码', '名称', '数量')
        return render(request, 'parts/part_upload.html', locals())

    def post(self, request):
        fpath, add_time = save_upload(request)
        rst = import_upload_erpbom(fpath, add_time)

        if 'error' in rst:
            title = '导入失败'
            info = rst['error']
        else:
            title = '导入成功'

        return render(request, 'info.html', locals())


# ===================================物料查找 相关视图=========================
# 采用bootstrap-table 的ajax方式
class PartFindView(View):
    def get(self, request):

        return render(request, 'parts/part_find_table.html', locals())

    def post(self, request):
        # 有2个查询库：物料库(编码、名称、含子零件...)、文件库(图号、发放单号、产品型号、申请单号)
        search = request.POST.get('search', None)
        field_type = request.POST.get('field_type', None)
        opt = request.POST.get('opt', 'AND')

        files = []
        if search:
            search = search.split(" ")
            files = Partfind_dict(search, field_type, opt)
        total = len(files)
        return JsonResponse({'total': total, 'rows': files})



class PartHistoryView(View):
    def post(self, request):
        search = request.POST.get('search', None)

        files = []
        if search:
            files = partHistoryFind(search)

        total = len(files)
        return JsonResponse({'total': total, 'rows': files})

# ===================================BOM查找 相关视图=========================

# 采用bootstrap-table

class BomFindView_Archive(View):
    def get(self, request):

        return render(request, 'parts/bom_find_table.html', locals())

    # 采用ajax方式提交
    def post(self, request):
        search = request.POST.get('search', None)
        field_type = request.POST.get('field_type', None)
        ar_id = request.POST.get('archive', None)
        rows = []
        if search:
            if field_type == 'CHILD':
                rows = childfind_current(search, 'ARCHIVE')
            elif field_type == 'PARENT':
                rows = parentfind_current(search, 'ARCHIVE')

        total = len(rows)
        # 这时候files只是类似字典的形式存储，但不能使用
        return JsonResponse({'total': total, 'rows': rows})


class BomHistoryView_Archive(View):
    def post(self, request):
        search = request.POST.get('search', None)
        field_type = request.POST.get('field_type', None)
        ar_id = request.POST.get('archive', None)
        rows = []
        if search:
            if field_type == 'CHILD':
                rows = childfind_model(search, 'ARCHIVE', ar_id)
            elif field_type == 'PARENT':
                rows = parentfind_model(search, 'ARCHIVE', ar_id)

        total = len(rows)
        return JsonResponse({'total': total, 'rows': rows})


class RootFindView_Archive(View):
    def post(self, request):
        search = request.POST.get('search', None)
        field_type = request.POST.get('field_type', None)
        rows = []
        if search:
            rows = rootfind(search, field_type, 'ARCHIVE')
        total = len(rows)
        return JsonResponse({'total': total, 'rows': rows})

#===================================ERPBOM查找================================




# ===================================成本 相关视图=========================

# 成本查询：根据提交的code,查询出成本
class CostFindView(View):
    def get(self, request):

        return render(request, 'parts/cost_find_table.html', locals())

    def post(self, request):
        search = request.POST.get('search', None)
        field_type = request.POST.get('field_type', None)
        opt = request.POST.get('opt', 'AND')
        rows = []
        if search and field_type:
            if field_type == 'BOM':
                bom = json.loads(search)  # 读取提交的物料列表

            else:  # 先去找物料
                search = search.split(" ")
                bom = Partfind_dict(search, field_type, opt)

            rows = bom_add_cost(bom)

        total = len(rows)
        # 这时候files只是类似字典的形式存储，但不能使用

        return JsonResponse({'total': total, 'rows': rows})


# 查询物料的所有成本
def costHistoryView(request):
    code = request.POST.get('code', '')

    # 先查找历史物料
    code_list = partHistoryFind(code)

    rows = find_cost_history(code_list)

    total = len(rows)
    return JsonResponse({'total': total, 'rows': rows})


# 成本计算：根据提交的bom进行计算
class CostRecalcView(View):
    def get(self, request):
        get_search = request.GET.get('search', None)
        get_type = request.GET.get('type', None)
        return render(request, 'parts/cost_find_table.html', locals())

    def post(self, request):
        search = request.POST.get('search', None)
        rows = []
        if search:
            s = json.loads(search)  # 读取提交的物料列表
            rows = bom_recalc_cost(bom=s)

        total = len(rows)
        # 这时候files只是类似字典的形式存储，但不能使用

        return JsonResponse({'total': total, 'rows': rows})


# ==========================设计更改========================

class ChangeFindView(View):
    def get(self, request):
        return render(request, 'parts/change_find_table.html', locals())

    def post(self, request):
        # 有2个查询库：物料库(编码、名称、含子零件...)、文件库(图号、发放单号、产品型号、申请单号)
        search = request.POST.get('search', None)
        draw = request.POST.get('draw', None)
        field_type = request.POST.get('field_type', None)
        ar_id = request.POST.get('archive', None)
        rows = []
        if search:
            if field_type == 'CHILD':
                #item = json.loads(search)
                rows = change_child(search,ar_id)
            elif field_type == 'PARENT':
                #item = json.loads(search)
                rows = change_parent(search,ar_id)
            elif field_type == 'ITEM':
                rows = change_find(search,draw, ar_id)

        total = len(rows)
        return JsonResponse({'total': total, 'rows': rows})



