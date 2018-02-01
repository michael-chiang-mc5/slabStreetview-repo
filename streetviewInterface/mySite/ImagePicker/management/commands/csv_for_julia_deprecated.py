from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import julia_harten_csv
import sys
class Command(BaseCommand):
    help = 'creates csv file for julia'

    def handle(self, *args, **options):
        julia_harten_csv()
        sys.exit(0)
