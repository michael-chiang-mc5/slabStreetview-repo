from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import *
import sys
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        g = GoogleOCR.objects.get(pk=48896)
        print(g.generate_signs())
