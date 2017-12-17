from django.core.management.base import BaseCommand, CommandError
from ImagePicker.db_interface import *
import sys
class Command(BaseCommand):
    help = 'arguments: priority, '

    def add_arguments(self, parser):
        parser.add_argument('option', nargs=1, type=str)

    def handle(self, *args, **options):
        option = options['option'][0]
        if option == 'priority':
            set_priority_bob()
        elif option == 'csv':
            write_csv_bob()
        else:
            print("Possible options: priority")
        sys.exit(0)
