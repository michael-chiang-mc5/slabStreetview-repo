from django.core.management.base import BaseCommand, CommandError
from ImagePicker.db_interface import *
import sys
class Command(BaseCommand):
    help = 'arguments: '

    def add_arguments(self, parser):
        parser.add_argument('option', nargs=1, type=str)

    def handle(self, *args, **options):
        option = options['option'][0]

        box_koreatown = {'lon1':-118.3100831509,'lat1':34.0634478683,'lon2':-118.2936894894,'lat2':34.0637256166}
        box_pico = {'lon1':-118.3013253068,'lat1':34.0470281939,'lon2':-118.2862271523,'lat2':34.0474548975}
        box_thaitown = {'lon1':-118.3126634746,'lat1':34.1015465926,'lon2':-118.2975653201,'lat2':34.1019508119}
        box_elmonte = {'lon1':-118.0633736043,'lat1':34.0625377556,'lon2':-118.0410432978,'lat2':34.0629210521}

        if option == 'write_signs':
            write_csv_sign(box_elmonte,'elmonte')
            write_csv_sign(box_thaitown,'thaitown')
            write_csv_sign(box_pico,'pico')
            write_csv_sign(box_koreatown,'koreatown')
        elif option == 'generate_signs':
            generate_signs()
        else:
            print("Possible options: ")
        sys.exit(0)
