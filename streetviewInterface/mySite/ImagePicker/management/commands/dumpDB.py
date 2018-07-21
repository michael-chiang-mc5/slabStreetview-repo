from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import dumpDB
import sys
from ImagePicker.models import *

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        print("writing MapPoint")
        dumpDB('MapPoint.csv',MapPoint)

        print("writing StreetviewImage")
        dumpDB('StreetviewImage.csv',StreetviewImage)

        print("writing GoogleOCR")
        dumpDB('GoogleOCR.csv',GoogleOCR)

        print("writing Sign")
        dumpDB('Sign.csv',Sign)
        sys.exit(0)
