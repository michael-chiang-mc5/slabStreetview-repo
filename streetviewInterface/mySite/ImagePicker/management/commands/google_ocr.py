from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import run_google_ocr
import sys
class Command(BaseCommand):
    help = 'saves mapPoint text file'

    def add_arguments(self, parser):
        parser.add_argument('max-api-calls', nargs=1, type=int)

    def handle(self, *args, **options):
        max_api_calls = options['max-api-calls'][0]
        run_google_ocr(max_api_calls)
        sys.exit(0)
