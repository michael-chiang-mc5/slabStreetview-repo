from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import *
import sys
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        num_high_priority = MapPoint.objects.filter(high_priority = True).count()
        print('num_high_priority=' , num_high_priority)

        numGoogleOCR = GoogleOCR.objects.all().count()
        print('numGoogleOCR=' , numGoogleOCR)



        # count the total number of signs
        print('num sign=' , Sign.objects.count())

        # Get the streetview images corresponding to signs
        streetviewImages = Sign.objects.values_list('boundingBox__streetviewImage',flat=True).distinct()
        print('num images=' , streetviewImages.count())

        bb = BoundingBox.objects.filter(streetviewImage__in=streetviewImages)
        print('num ctpn=', bb.count())
