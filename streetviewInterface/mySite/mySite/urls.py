"""mySite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')), # for description, see: https://docs.djangoproject.com/en/1.8/topics/auth/default/#using-the-views for description of django.contrib.auth.urls
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('myContent.urls', namespace='myContent')),
    url(r'^ImagePicker/', include('ImagePicker.urls', namespace='ImagePicker')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # TODO: disable this in production
