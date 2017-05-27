from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^routePicker/$', views.routePicker, name='routePicker'),
    url(r'^savePoint/$', views.savePoint, name='savePoint'),
    url(r'^listImage/$',  views.listImage, name='listImage'), #
    url(r'^listTextDetectorMetadata/$',  views.listTextDetectorMetadata, name='listTextDetectorMetadata'), #
    url(r'^listBoundingBoxMetadata/$',  views.listBoundingBoxMetadata, name='listBoundingBoxMetadata'), #
    url(r'^listBoundingBox/$',  views.listBoundingBox, name='listBoundingBox'), #
    url(r'^postBoundingBox/$',  views.postBoundingBox, name='postBoundingBox'),
    url(r'^postOCR/$',  views.postOCR, name='postOCR'), #
    url(r'^saveImages/$',  views.saveImages, name='saveImages'), #
    url(r'^picker/$', views.picker, name='picker'),

    url(r'^deleteAllBoundingBox/$',  views.deleteAllBoundingBox, name='deleteAllBoundingBox'), #
    url(r'^deleteAllStreetviewImages/$',  views.deleteAllStreetviewImages, name='deleteAllStreetviewImages'), #
    url(r'^deleteDuplicateMapPoints/$',  views.deleteDuplicateMapPoints, name='deleteDuplicateMapPoints'), #
    url(r'^runGoogleOCR_images/$',  views.runGoogleOCR_images, name='runGoogleOCR_images'), #

    url(r'^deleteAllMapPoints/$',  views.deleteAllMapPoints, name='deleteAllMapPoints'), #
    url(r'^adminPanel/$',  views.adminPanel, name='adminPanel'), #

    url(r'^boundingBox/(?P<boundingBox_pk>[0-9]+)/$',  views.boundingBox, name='boundingBox'), #
]
