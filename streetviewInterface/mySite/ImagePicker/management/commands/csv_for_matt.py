from django.core.management.base import BaseCommand, CommandError
from ImagePicker.db_interface import *
import sys
class Command(BaseCommand):
    help = 'creates csv file for matt bob project'
    def handle(self, *args, **options):
        temp()
        sys.exit(0)
