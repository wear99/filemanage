from django import forms
from .models import Archive,Product


def getproduct():
    prod = list(Product.objects.values_list('product', flat=True))
    ch = []    
    for p in prod:
        ch.append((p, p))
    return ch

# 发放表单
class ArchiveForm(forms.ModelForm):
    description = forms.CharField(label='发放说明',
        widget=forms.Textarea(attrs={'class': 'form-control'}))
    add_time = forms.DateField(
        label='发放日期', widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法        
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-control'}

    class Meta:
        model = Archive
        fields = ['archive_no', 'product',
                  'stage', 'description', 'file','add_time']


# 发放 文件上传表单
class ArchiveFileUploadForm(forms.Form):
    archive_id = forms.CharField()
    files = forms.FileField(
        label='图纸上传', widget=forms.FileInput(attrs={'multiple': True, 'onchange': 'fileselect();'}))
        
# 不用
class ArchiveDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法
        print(self.fields)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-group', 'readonly': True}

    class Meta:
        model = Archive
        fields = ['archive_no', 'product',
                  'stage', 'description', 'file', 'bom']


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法
        print(self.fields)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-control'}

    class Meta:
        model = Product
        fields = ['product_code', 'product_name', 'description']

