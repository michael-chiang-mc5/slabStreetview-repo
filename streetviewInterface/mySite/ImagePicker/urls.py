from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^picker/$', views.index, name='index'),
    url(r'^savePoint/$', views.savePoint, name='savePoint'),
    url(r'^listImage/$',  views.listImage, name='listImage'), #
    url(r'^listTextDetectorMetadata/$',  views.listTextDetectorMetadata, name='listTextDetectorMetadata'), #
    url(r'^listBoundingBoxMetadata/$',  views.listBoundingBoxMetadata, name='listBoundingBoxMetadata'), #
    url(r'^listBoundingBox/$',  views.listBoundingBox, name='listBoundingBox'), #
    url(r'^postBoundaryBox/$',  views.postBoundaryBox, name='postBoundaryBox'), #

    url(r'^deleteAllBoundingBox/$',  views.deleteAllBoundingBox, name='deleteAllBoundingBox'), #
    url(r'^deleteAllStreetviewImages/$',  views.deleteAllStreetviewImages, name='deleteAllStreetviewImages'), #
    url(r'^deleteAllMapPoints/$',  views.deleteAllMapPoints, name='deleteAllMapPoints'), #
    url(r'^adminPanel/$',  views.adminPanel, name='adminPanel'), #

]
