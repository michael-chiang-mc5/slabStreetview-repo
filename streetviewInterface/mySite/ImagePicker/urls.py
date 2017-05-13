from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^picker/$', views.index, name='index'),
    url(r'^savePoint/$', views.savePoint, name='savePoint'),
    url(r'^listImage/$',  views.listImage, name='listImage'), #
    url(r'^listTextDetectorMetadata/$',  views.listTextDetectorMetadata, name='listTextDetectorMetadata'), #
    url(r'^postBoundaryBox/$',  views.postBoundaryBox, name='postBoundaryBox'), #
]
