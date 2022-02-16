from django.urls import path
from tools.views import *

app_name = 'tools'
urlpatterns = [    
    path('checkcode/', CheckCodeView.as_view(), name='checkcode'),
    path('getstatus/<str:task_id>/',Get_task_status, name='getstatus'),
    

]
