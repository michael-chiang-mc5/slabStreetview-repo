from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^picker/$', views.index, name='index'),
    url(r'^save_image/(?P<latitude>-?\d+(?:\.\d+)?)/(?P<longitude>-?\d+(?:\.\d+)?)/(?P<heading>-?\d+(?:\.\d+)?)/(?P<pitch>-?\d+(?:\.\d+)?)/$',  views.save_image, name='save_image'),
    url(r'^list/$',  views.list, name='list') #
]
