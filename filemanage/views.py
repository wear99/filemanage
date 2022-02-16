from django.shortcuts import render
from django.views.generic import View

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


def page_not_found(request):
    return render(request, '404.html')


def page_error(request):
    return render(request, '500.html')


def permission_denied(request):
    return render(request, '403.html')
