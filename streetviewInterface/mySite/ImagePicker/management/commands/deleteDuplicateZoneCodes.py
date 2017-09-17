from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import *
import sys
class Command(BaseCommand):
    help = 'deletes duplicate zone codes'

    def handle(self, *args, **options):

        #mapPoints = MapPoint.objects.all()
        mapPoints = MapPoint.objects.filter(pk=69997)
        for mapPoint in mapPoints:
            try:
                mapPoint.get_zone_code()
            except:
                tags = MapTag.objects.filter(mapPoint=mapPoint,tag_type="zoning")
                tags.delete()
                print(tags)
                print(mapPoint.pk)
        sys.exit(0)
