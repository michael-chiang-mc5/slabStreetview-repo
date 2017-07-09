from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import syncImages
import sys

class Command(BaseCommand):
    help = 'syncs images'

    def handle(self, *args, **options):
        syncImages()
        sys.exit(0)
