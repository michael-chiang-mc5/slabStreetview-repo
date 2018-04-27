from django.core.management.base import BaseCommand, CommandError
from ImagePicker.db_interface import *
import sys
class Command(BaseCommand):
    """
    priority_matt sets priority to mapPoints associated with matt's black owned business dataset
    priority_julia sets priority to mapPoints associated with koreatown, thaitown, etc. boxes
    csv_matt writes csv files for matt's bob dataset
    csv_julia writes csv files for koreatown, thaitown, etc.
    """

    help = 'arguments: '

    def add_arguments(self, parser):
        parser.add_argument('option', nargs=1, type=str)

    def handle(self, *args, **options):
        option = options['option'][0]

        box_koreatown = {'lon1':-118.3100831509,'lat1':34.0634478683,'lon2':-118.2936894894,'lat2':34.0637256166}
        box_pico = {'lon1':-118.3013253068,'lat1':34.0470281939,'lon2':-118.2862271523,'lat2':34.0474548975}
        box_thaitown = {'lon1':-118.3126634746,'lat1':34.1015465926,'lon2':-118.2975653201,'lat2':34.1019508119}
        box_elmonte = {'lon1':-118.0633736043,'lat1':34.0625377556,'lon2':-118.0410432978,'lat2':34.0629210521}

        if option == 'priority_matt':
            set_priority_bob()
        elif option == 'csv_matt':
            write_csv_bob()
        elif option == 'priority_julia':
            set_priority_julia(box_elmonte)
            set_priority_julia(box_thaitown)
            set_priority_julia(box_pico)
            set_priority_julia(box_koreatown)
        elif option == 'priority_commercial':
            set_priority_fromJuliaBuffer()
            #set_priority()
        elif option == 'csv_julia':
            write_csv_julia(box_elmonte,'elmonte')
            write_csv_julia(box_thaitown,'thaitown')
            write_csv_julia(box_pico,'pico')
            write_csv_julia(box_koreatown,'koreatown')
        elif option == 'parcelVsLanguage':
            write_csv_parcelVsLanguage('all','all')
            #write_csv_parcelVsLanguage(box_elmonte,'elmonte')
            #write_csv_parcelVsLanguage(box_thaitown,'thaitown')
            #write_csv_parcelVsLanguage(box_pico,'pico')
            #write_csv_parcelVsLanguage(box_koreatown,'koreatown')
        else:
            print("Possible options: priority_matt, csv_matt, priority_julia, csv_julia, parcelVsLanguage")
        sys.exit(0)
