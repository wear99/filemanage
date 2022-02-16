from django.shortcuts import render

from django.shortcuts import render, redirect
from django.views.generic import View,FormView
from django.contrib.auth import authenticate, login, logout, models
#from django.contrib.auth.backends import ModelBackend
#from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse
from .models import UserProfile, UserLog
from .forms import LoginForm, RegisterForm, UserInfoForm

from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

# redirect(url地址)
# reverser(view方法名),返回一个url地址
# 模板中用 url view方法名,返回一个url地址

# 用户登录
class UserLoginView(View):
    def get(self, request):
        # 判断当前用户是否已经登录
        if request.user.is_authenticated:
            #messages.success(request, message='已经登录')
            return redirect('users:userinfo')
        else:
            form = LoginForm()
            return render(request, 'users/user_login.html', locals())

    def post(self, request):
        redirect_to = request.GET.get('next', 'index')
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            rem = form.cleaned_data["remember_me"]

            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    msg = '账号未激活，请联系管理员'
                    return render(request, r'users/user_login.html', locals())
                elif user.role == '禁止':
                    msg = '账号被禁用!'
                    return render(request, r'users/user_login.html', locals())
                else:
                    login(request, user)
                    #messages.success(request,message='登录成功')
                    #day=datetime.now()+timedelta(days=30)
                    if rem:
                        # 在设定时间后过期，如果输入整数，则代表连接空闲多少秒后session过期
                        # 设为None则依赖全局设定,默认2周
                        request.session.set_expiry(None)
                    else:
                        # 设为0，则代表浏览器关闭即失效；
                        request.session.set_expiry(0)

                    return redirect(redirect_to)
            else:
                msg = "用户名或密码错误！"                
                return render(request, 'users/user_login.html', locals())
        else:
            return render(request, "users/user_login.html", locals())


# 用户退出

class UserLogoutView(LogoutView):
    next_page='/'

# 管理员对用户的操作相关视图(管理员可见)
# 用户列表

'''
class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != '2' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            users = UserProfile.objects.filter(Q(userno__icontains=search) | Q(username__icontains=search)
                                               | Q(department__icontains=search), is_superuser=0
                                               )  # 排除超级管理员
        else:
            users = UserProfile.objects.filter(
                is_superuser=0).order_by('-role', 'userno')  # 排除超级管理员

        return render(request, 'user_list.html', {'p_contents': p_contents, 'start': start, 'search': search})
'''

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('user:userinfo')
        else:
            form = RegisterForm()
            return render(request, 'users/register.html', locals())

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm = form.cleaned_data['confirm_password']
            email = form.cleaned_data['email']
            if confirm != password:
                msg = '两次密码不一致!'
                return render(request, 'users/register.html', locals())
            else:
                same_email = UserProfile.objects.filter(email=email)
                if same_email:
                    msg = '邮箱已存在!'
                    return render(request, 'users/register.html', locals())
            user = form.save()
            user.set_password(user.password)
            user.save()
            return redirect('login')
        else:
            return render(request, 'users/register.html', locals())


class UserInfoView(LoginRequiredMixin, View):
    #initial = {'name': 'nanxiang', 'age': '18'}

    '''
    template_name = 'users/userinfo.html'
    form_class = UserInfoForm
    
    initial = request.user
    def form_valid(self, form):
        pass

    ''' 
    def get(self,request):
        #user = UserProfile.objects.filter(username=request.user.username)
        form = UserInfoForm(instance=request.user)
        return render(request, 'users/userinfo.html', locals())



