from django.core.management.base import BaseCommand, CommandError
import sys
from ImagePicker.models import *
from gmplot import gmplot

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        gmap = gmplot.GoogleMapPlotter(34.04464406169281, -118.27687109859778, 13)


        lng = [r.longitude() for r in Sign.objects.all()]
        lat = [r.latitude() for r in Sign.objects.all()]


        gmap.scatter(lat, lng, '#3B0B39', size=40, marker=False)
        # Draw
        gmap.draw("my_map.html")

        sys.exit(0)
