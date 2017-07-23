from django.core.management.base import BaseCommand, CommandError
import sys
from ImagePicker.views import get_census_tracts
class Command(BaseCommand):
    help = 'saves mapPoint text file'

    def handle(self, *args, **options):
        get_census_tracts()
        sys.exit(0)
