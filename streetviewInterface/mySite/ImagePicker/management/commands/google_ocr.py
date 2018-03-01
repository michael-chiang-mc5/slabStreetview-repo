from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import run_google_ocr
import sys
class Command(BaseCommand):
    help = 'python manage.py google_ocr maxCalls priority(1=True)'

    def add_arguments(self, parser):
        parser.add_argument('max-api-calls', nargs=2, type=int)

    def handle(self, *args, **options):
        max_api_calls = options['max-api-calls'][0]
        priority = options['max-api-calls'][1]
        if priority is 0:
            priority = False
        else:
            priority = True
        run_google_ocr(max_api_calls,priority)
        sys.exit(0)
