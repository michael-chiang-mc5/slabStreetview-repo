from django.core.management.base import BaseCommand, CommandError
from ImagePicker.parcel_boundary_helper import *
import sys
class Command(BaseCommand):
    """
    Comment here
    """

    def handle(self, *args, **options):
        import_parcel_boundary_to_db()
        sys.exit(0)
