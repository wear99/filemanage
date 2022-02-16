"""filemanage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import IndexView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),    
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('files/', include(('files.urls', 'files'), namespace='files')),
    path('parts/', include(('parts.urls', 'parts'), namespace='parts')),
    path('archive/', include(('archive.urls', 'archive'), namespace='archive')),
    path('application/', include(('application.urls','application'), namespace='application')), 
    path('tools/', include(('tools.urls','tools'), namespace='tools')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#handler403 = permission_denied
#handler404 = page_not_found
#handler500 = page_error
