from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import run_google_ocr
import sys
class Command(BaseCommand):
    help = 'saves mapPoint text file'

    def handle(self, *args, **options):
        run_google_ocr()
        sys.exit(0)
