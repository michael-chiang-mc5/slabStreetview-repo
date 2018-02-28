from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import *
import sys
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        # count the total number of signs
        print('num sign=' , Sign.objects.count())

        # Get the streetview images corresponding to signs
        streetviewImages = Sign.objects.values_list('boundingBox__streetviewImage',flat=True).distinct()
        print('num images=' , streetviewImages.count())

        bb = BoundingBox.objects.filter(streetviewImage__in=streetviewImages)
        print('num ctpn=', bb.count())
