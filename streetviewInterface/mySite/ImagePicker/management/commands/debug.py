from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import *
import sys
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        g = GoogleOCR.objects.filter(streetviewImage__mapPoint__longitude__gte=-118.171126, \
                                    streetviewImage__mapPoint__longitude__lte=-118.13657, \
                                    streetviewImage__mapPoint__latitude__gte=33.941089, \
                                    streetviewImage__mapPoint__latitude__lte=33.955671, \
                                                                    )
        print(g.count())
        print(g.order_by('-pk')[1])
