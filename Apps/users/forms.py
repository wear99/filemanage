from django import forms
from .models import UserProfile


# 定义登录时表单验证
class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username', 'autofocus':'True'}), required=True)
    password = forms.CharField(label='密码', max_length=64, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}), required=True)
    remember_me = forms.BooleanField(label='记住我', required=False, widget=forms.CheckboxInput(attrs={'class': 'checkbox mb-3'}))

# 定义用户修改密码时表单验证
class UserPwdModifyForm(forms.Form):
    pwd1 = forms.CharField()
    pwd2 = forms.CharField()

# 使用模型自动创建表单，具有表单和模型双重验证功能
# 当调用form.save时，自动保存到数据库

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label='再次输入密码', min_length=6,max_length=128, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # 通过初始化程序自动设置字段样式
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法
        print(self.fields)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-control'}

    class Meta:
        model=UserProfile
        fields = ['username', 'ch_name', 'password',
                  'confirm_password', 'email', 'phone', 'department']
        widgets={            
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),           
            
        }

class UserInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法
        print(self.fields)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-control','readonly':True}
    class Meta:
        model=UserProfile
        fields = ['username', 'ch_name', 'email', 'phone',
                  'department', 'groups', 'date_joined']


