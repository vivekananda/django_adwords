from django.core.management.base import BaseCommand, CommandError

from django_adwords.adwords_utils import Csv_interactor


class Command( BaseCommand ):
    args = '<csv file stored from adwords editor>'
    help = 'parses the file and populates db'

    def handle( self, *args, **options ):
        if not args:
            print "usage:: python manage.py load_data_from_csv data_files/ATC+2012-11-14.csv"
            import sys
            sys.exit()
            
        csv_file = open( args[0], 'rU' )
        ci = Csv_interactor()
        ci.load_csv_file(csv_file)

if __name__ == "__main__":
    import sys
    if len( sys.argv ) < 2:
        print "syntax:: python sema/process_csv.py  <csv file>"
#    process_csvfile( sys.argv[1] )

