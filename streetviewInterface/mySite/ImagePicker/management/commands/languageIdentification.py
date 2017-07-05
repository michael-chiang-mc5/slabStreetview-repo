from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import saveImages_async
import sys
class Command(BaseCommand):
    help = 'runs language identification on google ocr results'

    def handle(self, *args, **options):
        runLanguageIdentifiction_async()
        sys.exit(0)
