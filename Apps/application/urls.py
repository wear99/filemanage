from django.urls import path
from .views import AppListView, ApprovalView, AppAddView, ProvidfileView, AppDetailView, App_file_download

app_name = 'application'
urlpatterns = [    
    path('list/', AppListView.as_view(), name='list'),    
    path('new/', AppAddView.as_view(), name='new'),
    path('detail/<str:pk>/', AppDetailView.as_view(), name='detail'),
    path('approval/<str:pk>/', ApprovalView.as_view(), name='approval'),
    path('provid/<str:pk>/', ProvidfileView.as_view(), name='provid'),
    path('download/', App_file_download, name='download')

]
    
