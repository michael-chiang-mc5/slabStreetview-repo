from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import dumpDB
import sys
from ImagePicker.models import *

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        dumpDB('Sign.csv',Sign)
        sys.exit(0)
