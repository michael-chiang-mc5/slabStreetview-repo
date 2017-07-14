from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import write_mapPoint
import sys
class Command(BaseCommand):
    help = 'saves mapPoint text file'

    def handle(self, *args, **options):
        write_mapPoint()
        sys.exit(0)
