from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^routePicker/$', views.routePicker, name='routePicker'),
    url(r'^savePoint/$', views.savePoint, name='savePoint'),
    url(r'^listImage/$',  views.listImage, name='listImage'), #
    url(r'^list_CTPN_metadata/$',  views.list_CTPN_metadata, name='list_CTPN_metadata'), #
    url(r'^list_crnn_metadata/$',  views.list_crnn_metadata, name='list_crnn_metadata'), #
    url(r'^list_ECN_metadata/$',  views.list_ECN_metadata, name='list_ECN_metadata'), #
    url(r'^listBoundingBox/$',  views.listBoundingBox, name='listBoundingBox'), #
    url(r'^postBoundingBox/$',  views.postBoundingBox, name='postBoundingBox'),
    url(r'^postOCR/$',  views.postOCR, name='postOCR'), #
    url(r'^postECN/$',  views.postECN, name='postECN'), #

    url(r'^saveImages/$',  views.saveImages, name='saveImages'), #
    url(r'^picker/$', views.picker, name='picker'),
    url(r'^deleteAllScriptIdentification/$',  views.deleteAllScriptIdentification, name='deleteAllScriptIdentification'), #

    url(r'^deleteAllBoundingBox/$',  views.deleteAllBoundingBox, name='deleteAllBoundingBox'), #
    url(r'^deleteAllStreetviewImages/$',  views.deleteAllStreetviewImages, name='deleteAllStreetviewImages'), #
    url(r'^deleteDuplicateMapPoints/$',  views.deleteDuplicateMapPoints, name='deleteDuplicateMapPoints'), #
    url(r'^runGoogleOCR_images/$',  views.runGoogleOCR_images, name='runGoogleOCR_images'), #
    url(r'^runGoogleOCR_boundingBoxes/$',  views.runGoogleOCR_boundingBoxes, name='runGoogleOCR_boundingBoxes'), #

    url(r'^deleteAllOcr/$',  views.deleteAllOcr, name='deleteAllOcr'), #

    url(r'^deleteAllMapPoints/$',  views.deleteAllMapPoints, name='deleteAllMapPoints'), #
    url(r'^adminPanel/$',  views.adminPanel, name='adminPanel'), #
    url(r'^deleteStreetviewImage/(?P<streetviewImage_pk>[0-9]+)/$',  views.deleteStreetviewImage, name='deleteStreetviewImage'), #
    url(r'^boundingBox/(?P<boundingBox_pk>[0-9]+)/$',  views.boundingBox, name='boundingBox'), #
]
