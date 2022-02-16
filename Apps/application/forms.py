from django import forms
from .models import Application


# 图纸申请表单
class ApplicationForm(forms.ModelForm):
    archive_no = forms.CharField(label='发放单号', required=False,
                                 widget=forms.Textarea(attrs={'class': 'form-control'}))
    bom = forms.FileField(
        label='申请物料清单', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    add_time = forms.DateField(
        label='申请日期', widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法
        print(self.fields)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-control'}

    class Meta:
        model = Application
        fields = ['product', 'description', 'bom','add_time']


class ApprovalForm(forms.Form):
    result = forms.IntegerField(label='批准')
    remark = forms.CharField(required=False, label='审核信息')
    app_id = forms.CharField()


class ProvidForm(forms.Form):
    appno = forms.CharField()
    providlist = forms.CharField(label='', required=False)
