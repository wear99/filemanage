from django.urls import path

from .views import *

app_name = 'archive'
urlpatterns = [    
    path('archivefind/', ArchiveFindView.as_view(), name='archivefind'),
    path('new/', ArchiveAddView.as_view(), name='new'),
    
    path('detail/<str:pk>/',ArchiveDetailView.as_view(), name='detail'),    
    path('edit/<str:pk>/', ArchiveEditView.as_view(), name='edit'),

    path('bomupload/<str:pk>/', ArchiveBomUploadView.as_view(), name='bomupload'),
    path('bomdownload/<str:pk>/', DownloadBom, name='bomdownload'), 
    path('bomview/<str:pk>/', ArchiveBomView.as_view(), name='bomview'),

    path('upload/<str:ar_id>/', ArchiveUploadFileView.as_view(), name='fileupload'),
    path('filelist/<str:pk>/', ArchiveFileListView.as_view(), name='filelist'),

]
    
