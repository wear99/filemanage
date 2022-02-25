from django.urls import path
from parts.views import *

app_name = 'parts'
urlpatterns = [
    path('partfind/', PartFindView.as_view(), name='partfind'),
    path('parthistory/', PartHistoryView.as_view(), name='parthistory'),

    path('bomfind/', BomFindView_Archive.as_view(), name='bomfind'),
    path('bomhistory/', BomHistoryView_Archive.as_view(), name='bomhistory'),
    path('rootfind/', RootFindView_Archive.as_view(), name='rootfind'),

          
    path('costfind/', CostFindView.as_view(), name='costfind'), 
    path('costhistory/', costHistoryView, name='costhistory'),
    path('costrecalc/', CostRecalcView.as_view(), name='costrecalc'),

    path('changefind/', ChangeFindView.as_view(), name='changefind'),

    path('uploadpart/', UploadPartView.as_view(), name='uploadpart'),
    path('uploadcost/', UploadCostView.as_view(), name='uploadcost'),
    path('uploaderpbom/', UploadErpBomView.as_view(), name='uploaderpbom'),
    path('uploadfile/', uploadFileView, name='uploadfile'),    

]
