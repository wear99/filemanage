from django.urls import path

from .views import *
# 匹配变量参数   (?P<变量名>规则)   (?P<int>\d+)，表示匹配到多个数字，给变量int
# 

app_name = 'files'
urlpatterns = [
    path('filefind/', FileFindView_table.as_view(), name='filefind'),
    path('uploadfile_archive/', FileUploadView_archive.as_view(),
         name='uploadfile_archive'),
    #path('download/<str:file_id>/', DownloadFile, name='download'),
    #path('downloads/', DownloadFile_zip, name='downloads'),
    path('view/<str:file_id>/', ViewFile, name='view'),
]
    
