from django.core.management.base import BaseCommand, CommandError

import csv
from cherrypy.test.test_refleaks import data
from StringIO import StringIO
from django_adwords.models import Campaign, Client, Adgroup, Keyword, Criterion, \
    CRITERION_TYPE_ADGROUP_POSITIVE, Record_change, Ad
from sema.models import Keyword_suggestion, Em_bm_campaign_pair


class Command( BaseCommand ):
    args = '<csv file name to be nerated from adwords editor>'
    help = 'Generates a file that can be uploaded to adwords editor'
    def handle( self, *args, **options ):
        if not args:
                print "usage:: python manage.py load_data_from_csv data_files/ATC+2012-11-14.csv"
                import sys
                sys.exit()

        csv_file = open( args[0], 'wb' )
        writer = csv.writer( csv_file, dialect = 'excel-tab', delimiter = '\t', quotechar = '|' )

        kw_sugs = Keyword_suggestion.objects.filter( selected_suggestion__isnull = False, pushed_to_adwords = False )
        header = ['Campaign', 'Campaign Daily Budget', 'Languages', 'ID', 'Location', 'Ad Schedule', 'Networks', 'Ad Group', 'Max CPC', 'Display Network Max CPC', 'Max CPM', 'CPA Bid', 'Max CPC Multiplier', 'Display Network Max CPC Multiplier', 'Max CPM Multiplier', 'Flexible Reach', 'Keyword', 'Audience', 'Criterion Type', 'First Page CPC', 'Top Of Page CPC', 'Quality Score', 'Headline', 'Description Line 1', 'Description Line 2', 'COMPANY_NAME', 'PHONE_NUMBER', 'ADDRESS LINE 1', 'ADDRESS LINE 2', 'CITY', 'STATE', 'POSTAL_CODE', 'COUNTRY_CODE', 'map_icon', 'Source', 'Link Text', 'Order', 'Display URL', 'Destination URL', 'Campaign Status', 'AdGroup Status', 'Status', 'Approval Status', 'Suggested Changes', 'Comment']

        writer.writerow( header )
        for sug in kw_sugs:
            row = [''] * len( header )
            row[header.index( 'Campaign', )] = sug.selected_suggestion.campaign.name
            row[header.index( 'Max CPC' ) ] = 4
            row[header.index( 'Ad Group' )] = sug.selected_suggestion.name
            row[header.index( 'Keyword' )] = sug.text
            row[header.index( 'Criterion Type' )] = 'Exact'
            row[header.index( 'Comment' )] = "SEMA"
            writer.writerow( row )
            ######### add -ve keyword
            campaign_pair = Em_bm_campaign_pair.objects.get( exact_match_campaign__campaign = sug.selected_suggestion.campaign )
            bm_adgroup = Adgroup.objects.get( campaign = campaign_pair.broad_match_campaign.campaign, name = sug.selected_suggestion.name )
            row[header.index( 'Campaign', )] = campaign_pair.broad_match_campaign.campaign.name
            row[header.index( 'Max CPC' ) ] = ''
            row[header.index( 'Ad Group' )] = bm_adgroup.name
            row[header.index( 'Keyword' )] = "-%s" % sug.text
            writer.writerow( row )

        csv_file.close()
