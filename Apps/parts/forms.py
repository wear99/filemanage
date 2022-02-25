from django import forms

# 物料查找表单
class PartFindForm(forms.Form):
    ftype = (('union', '模糊'), ('draw', '图号'),  ('code', '编码'),
             ('partname', '名称'), ('remark', '备注'))

    tp = forms.ChoiceField(label='查询方式', choices=ftype)
    tp.widget.attrs = {'class': 'form-control'}
    search = forms.CharField(label='', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    ch = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    vd = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "checkbox mb-3"}), required=False)
    has = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "checkbox mb-3", 'checked': 'true'}), required=False)
    opt = forms.ChoiceField(choices=(('AND', 'AND'), ('OR', 'OR')))
    opt.widget.attrs = {'class': 'form-control'}


class FileUploadForm(forms.Form): # 物料库上传
    file = forms.FileField(label='物料表')
    add_time = forms.DateTimeField(
        label='导入日期', widget=forms.DateInput(attrs={'type': 'date'}))
    filetype=forms.CharField()


# 发放 BOM上传表单
class ArchiveBomUploadForm(forms.Form):
    archive_id = forms.CharField()
    bom=forms.FileField()



    
