from django.core.management.base import BaseCommand, CommandError
import sys
from ImagePicker.models import *
from gmplot import gmplot

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        gmap = gmplot.GoogleMapPlotter(34.04464406169281, -118.27687109859778, 13)



        lng = [r.longitude_val() for r in MapPoint.objects.all()]
        lat = [r.latitude_val() for r in MapPoint.objects.all()]
        print("done extracting lng/lat")

        gmap.scatter(lat, lng, '#3B0B39', size=40, marker=False)
        print("done making scatter")
        # Draw
        gmap.draw("media/my_map.html")

        sys.exit(0)
