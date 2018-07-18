from django.core.management.base import BaseCommand, CommandError
from ImagePicker.db_interface import *
import sys
class Command(BaseCommand):
    help = 'arguments: '

    def add_arguments(self, parser):
        parser.add_argument('option', nargs=1, type=str)

    def handle(self, *args, **options):
        option = options['option'][0]

        if option == 'generate_signs_fresh':
            generate_signs(fresh=True)
        elif option == 'generate_signs':
            generate_signs()
        else:
            print("Possible options: generate_signs, write_signs")
        sys.exit(0)
