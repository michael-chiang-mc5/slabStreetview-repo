from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import saveImages_async
class Command(BaseCommand):
    help = 'saves images'

    def handle(self, *args, **options):
        saveImages_async()
