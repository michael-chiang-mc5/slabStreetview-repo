from django.core.management.base import BaseCommand, CommandError
from ImagePicker.db_interface import *
import sys
class Command(BaseCommand):
    help = 'arguments: '

    def add_arguments(self, parser):
        parser.add_argument('option', nargs=1, type=str)

    def handle(self, *args, **options):
        option = options['option'][0]

        if option == 'write_signs':
            write_csv_sign()
        elif option == 'generate_signs':
            generate_signs()
        else:
            print("Possible options: ")
        sys.exit(0)
