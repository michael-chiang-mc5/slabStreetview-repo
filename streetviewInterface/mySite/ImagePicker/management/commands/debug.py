from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import *
import sys
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        min_lat = ParcelBoundary.objects.order_by('lat').first().lat
        max_lat = ParcelBoundary.objects.order_by('lat').last().lat
        min_lng = ParcelBoundary.objects.order_by('lng').first().lng
        max_lng = ParcelBoundary.objects.order_by('lng').last().lng

        print(min_lat,max_lat)
        print(min_lng,max_lng)


        min_lat = MapPoint.objects.filter().values_list('latitude').annotate(Min('latitude')).order_by('latitude').first()[0]
        min_lng = MapPoint.objects.filter().values_list('longitude').annotate(Min('longitude')).order_by('longitude').first()[0]
        max_lat = MapPoint.objects.filter().values_list('latitude').annotate(Min('latitude')).order_by('latitude').last()[0]
        max_lng = MapPoint.objects.filter().values_list('longitude').annotate(Min('longitude')).order_by('longitude').last()[0]

        print(min_lat,max_lat)
        print(min_lng,max_lng)

