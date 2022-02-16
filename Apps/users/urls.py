from django.urls import path

from .views import UserLoginView, UserLogoutView, RegisterView, UserInfoView
#from .views import UserListView, UserAddView, UserDetailView, UserModifyView, UserResetPwd, UserPwdModifyView
#from .views import UserOperateView

app_name='users'
urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('userinfo/', UserInfoView.as_view(), name='userinfo'),
    
]
