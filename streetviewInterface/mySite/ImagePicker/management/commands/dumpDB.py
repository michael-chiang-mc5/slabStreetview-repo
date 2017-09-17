from django.core.management.base import BaseCommand, CommandError
from ImagePicker.views import dumpDB
import sys
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        dumpDB()
        sys.exit(0)
