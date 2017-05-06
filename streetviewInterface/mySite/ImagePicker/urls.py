from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^picker/$', views.index, name='index'),
    url(r'^listImage/$',  views.listImage, name='listImage') #
]
