from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^index_figures/$', views.index_figures, name='index_figures'),
    url(r'^post_zoning/$', views.post_zoning, name='post_zoning'),

    url(r'^routePicker/$', views.routePicker, name='routePicker'),
    url(r'^crawler/$', views.crawler, name='crawler'),
    url(r'^bfs/$', views.bfs, name='bfs'),
    url(r'^get_current_bfs_queue_item/$', views.get_current_bfs_queue_item, name='get_current_bfs_queue_item'),
    url(r'^initialize_bfs/$', views.initialize_bfs, name='initialize_bfs'),
    url(r'^savePoint/$', views.savePoint, name='savePoint'),
    url(r'^listImage/(?P<streetviewImage_pk>[0-9]+)/$',  views.listImage, name='listImage'), #
    url(r'^listImage_AIN/(?P<streetviewImage_pk>[0-9]+)/$',  views.listImage_AIN, name='listImage_AIN'), #

    url(r'^listImages/$',  views.listImages, name='listImages'), #

    url(r'^read_mapPoint/$',  views.read_mapPoint, name='read_mapPoint'), #

    url(r'^list_CTPN_metadata/$',  views.list_CTPN_metadata, name='list_CTPN_metadata'), #
    url(r'^list_crnn_metadata/$',  views.list_crnn_metadata, name='list_crnn_metadata'), #
    url(r'^list_ECN_metadata/$',  views.list_ECN_metadata, name='list_ECN_metadata'), #
    url(r'^metadata_zoning/$', views.metadata_zoning, name='metadata_zoning'),


    url(r'^listBoundingBox/$',  views.listBoundingBox, name='listBoundingBox'), #
    url(r'^postBoundingBox/$',  views.postBoundingBox, name='postBoundingBox'),
    url(r'^postOCR/$',  views.postOCR, name='postOCR'), #

    url(r'^image_saver_metadata/$',  views.image_saver_metadata, name='image_saver_metadata'), #
    url(r'^set_image_pending/$',  views.set_image_pending, name='set_image_pending'), #
    url(r'^set_image_uploaded/$',  views.set_image_uploaded, name='set_image_uploaded'), #
    url(r'^deletePending/$',  views.deletePending, name='deletePending'), #


    url(r'^picker/$', views.picker, name='picker'),

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
    url(r'^boundingBox_expanded/(?P<boundingBox_pk>[0-9]+)/$',  views.boundingBox_expanded, name='boundingBox_expanded'), #


    url(r'^overlayBox/(?P<image_pk>[0-9]+)/(?P<x1>[0-9]+)/(?P<x2>[0-9]+)/(?P<y1>[0-9]+)/(?P<y2>[0-9]+)/$',  views.overlayBox, name='overlayBox'), #

    url(r'^AIN_to_image/(?P<AIN>[0-9]+)/$',  views.AIN_to_image, name='AIN_to_image'), #


    url(r'^runGoogleOCR_image/(?P<pk>[0-9]+)/$',  views.runGoogleOCR_image, name='runGoogleOCR_image'), #


    url(r'^runGoogleOCR_randomImage/$',  views.runGoogleOCR_randomImage, name='runGoogleOCR_randomImage'), #

    url(r'^runGoogleOCR_boundingBox/(?P<boundingBox_pk>[0-9]+)/$',  views.runGoogleOCR_boundingBox, name='runGoogleOCR_boundingBox'), #
    url(r'^deleteOcrText/(?P<ocrtext_pk>[0-9]+)/$',  views.deleteOcrText, name='deleteOcrText'), #
    url(r'^deleteBoundingBox/(?P<pk>[0-9]+)/$',  views.deleteBoundingBox, name='deleteBoundingBox'), #

    url(r'^benchmarkingPanel/$',  views.benchmarkingPanel, name='benchmarkingPanel'), #
    url(r'^annotateRandomBoundingBox/$',  views.annotateRandomBoundingBox, name='annotateRandomBoundingBox'), #
    url(r'^postManualOCR/$',  views.postManualOCR, name='postManualOCR'), #
    url(r'^runGoogleOCR_manualOCR/$',  views.runGoogleOCR_manualOCR, name='runGoogleOCR_manualOCR'), #

    url(r'^runLanguageIdentifiction/$',  views.runLanguageIdentifiction, name='runLanguageIdentifiction'), #
    url(r'^deleteAllOcrLanguage/$',  views.deleteAllOcrLanguage, name='deleteAllOcrLanguage'), #
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # TODO: disable this in production
