from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import *
import sys
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        s = Sign.objects.all()
        print(s[0])
