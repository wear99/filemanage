from django import forms


class testForm(forms.Form):
    name=forms.CharField()
    file = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True, 'class': 'form-control'}))

class FileFindForm(forms.Form):
    ftype = (('filename', '图号'), ('product', '产品名称'),
             ('archive', '发放单号'), ('designer', '设计者'),)

    tp = forms.ChoiceField(label='查询方式', choices=ftype)
    tp.widget.attrs = {'class': 'form-control'}
    search = forms.CharField(label='',required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))   
    ch = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    vd = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "checkbox mb-3"}), required=False)
    has = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "checkbox mb-3", 'checked': 'true'}), required=False)
    
    opt = forms.ChoiceField(choices=(('AND', 'AND'), ('OR', 'OR')))
    opt.widget.attrs = {'class': 'form-control'}

