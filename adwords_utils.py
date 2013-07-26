from adspygoogle.adwords.AdWordsClient import AdWordsClient
from adspygoogle.common import Utils
import os
import time
import datetime

import csv
from StringIO import StringIO
from django_adwords.models import Campaign, Client, Adgroup, Keyword, Criterion,\
    CRITERION_TYPE_ADGROUP_POSITIVE, Record_change, Ad
from django.db import transaction

# https://developers.google.com/adwords/api/docs/reference/latest/AdExtensionOverrideService

MATCH_TYPE_EXACT = 'exact'
MATCH_TYPE_BROAD = 'broad'
MATCH_TYPE_PHRASE = 'phrase'

KEYWORD_TYPE_POSITIVE = 'biddableadgroupcriterion'
KEYWORD_TYPE_NEGATIVE = 'negativeadgroupcriterion'
 
class Adwords_interactor():
    '''
    A class to interact with Adwords through API, will have funcitons to read data from Adwords like campaigns, adgroups, ads, keywords and 
    Also, this class will have functions to push data to adwords
    '''
    DEBUG = False
    PAGE_SIZE=100
    #ADWORDS_URL = 'https://adwords-sandbox.google.com'
    ADWORDS_URL = 'https://adwords.google.com'
    ADWORDS_API_VERSION = 'v201209'
    
    def  __init__(self):
        self.client = AdWordsClient( path = 'ext/adwords_api_python_15.5.0' )
#    campaign_service = client.GetCampaignService(ADWORDS_URL, ADWORDS_API_VERSION)
    
    def get_campaign_service(self):
        if not self.__dict__.get('campaign_service',None):
            self.campaign_service = self.client.GetCampaignService(self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        return self.campaign_service
    
    def get_all_campaigns(self,client_id=None):
        '''
        Get all the 
        '''
        if client_id:
#            ToDo: if client id is passed need to get the campaigns for this client
            pass
        # Construct selector and get all campaigns.
        offset = 0
        selector = {
            'fields': ['Id', 'Name', 'Status'],
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(self.PAGE_SIZE)
            }
        }
        campaigns = []
        more_pages = True
        while more_pages:
            page = self.get_campaign_service().Get(selector)[0]
            
            # Display results.
            if 'entries' in page:
                campaigns.extend(page['entries'])
            offset += self.PAGE_SIZE
            selector['paging']['startIndex'] = str(offset)
            more_pages = offset < int(page['totalNumEntries'])
        return campaigns
    
    def add_campaign(self):
        
        pass
    
    def create_account(self): 
      # Initialize appropriate service.
      managed_customer_service = self.client.GetManagedCustomerService(
          'https://adwords-sandbox.google.com', self.ADWORDS_API_VERSION)
    
      today = datetime.datetime.today().strftime('%Y%m%d %H:%M:%S')
      # Construct operations and add campaign.
      operations = [{
          'operator': 'ADD',
          'operand': {
              'name': 'Account created with ManagedCustomerService on %s' % today,
              'currencyCode': 'INR',
              'dateTimeZone': 'India/Asia',
          }
      }]
    
      # Create the account. It is possible to create multiple accounts with one
      # request by sending an array of operations.
      accounts = managed_customer_service.Mutate(operations)[0]
    
      # Display results.
      for account in accounts['value']:
        print ('Account with customer ID \'%s\' was successfully created.'
               % account['customerId'])
    
      print
      print ('Usage: %s units, %s operations' % (self.client.GetUnits(),
                                                 self.client.GetOperations()))
        
         
    def get_campaign_stats(self):
      # Initialize appropriate service.
      campaign_service = self.client.GetCampaignService(
          'https://adwords-sandbox.google.com', 'v201109')
    
      # Construct selector and get all campaigns.
      offset = 0
      selector = {
          'fields': ['Id', 'Name', 'Impressions', 'Clicks', 'Cost', 'Ctr'],
          'predicates': [{
              'field': 'Impressions',
              'operator': 'GREATER_THAN',
              'values': ['0']
          }],
          'dateRange': {
              'min': (datetime.datetime.now() -
                      datetime.timedelta(7)).strftime('%Y%m%d'),
              'max': (datetime.datetime.now() -
                      datetime.timedelta(1)).strftime('%Y%m%d')
          },
          'paging': {
              'startIndex': str(offset),
              'numberResults': str(self.PAGE_SIZE)
          }
      }
    
      more_pages = True
      while more_pages:
        page = campaign_service.Get(selector)[0]
        
        # Display results.
        if 'entries' in page:
          for campaign in page['entries']:
            print ('Campaign with id \'%s\' and name \'%s\' had the following '
                   'stats during the last week.' % (campaign['id'],
                                                    campaign['name']))
            print '  Impressions: %s' % campaign['campaignStats']['impressions']
            print '  Clicks: %s' % campaign['campaignStats']['clicks']
            cost = int(campaign['campaignStats']['cost']['microAmount']) / 1000000
            print '  Cost: %.02f' % cost
            ctr = float(campaign['campaignStats']['ctr']) * 100
            print '  CTR: %.02f %%' % ctr
        else:
          print 'No matching campaigns were found.'
        offset += self.PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])
    
      print
      print ('Usage: %s units, %s operations' % (self.client.GetUnits(),
                                                 self.client.GetOperations()))
    
    def get_ad_groups(self,campaign_id):
        # Initialize appropriate service.
        ad_group_service = self.client.GetAdGroupService(
            self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        
        # Construct selector and get all ad groups.
        adgroups = []
        offset = 0
        selector = {
            'fields': ['Id', 'Name', 'Status'],
            'predicates': [
                {
                    'field': 'CampaignId',
                    'operator': 'EQUALS',
                    'values': [str(campaign_id)]
                },
                {
                    'field': 'Status',
                    'operator': 'EQUALS',
                    'values': ['ENABLED']
                }
            ],
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(self.PAGE_SIZE)
            }
        }
        more_pages = True
        while more_pages:
            page = ad_group_service.Get(selector)[0]
        
            # get results.
            if 'entries' in page:
                adgroups.extend(page['entries'])
#              for ad_group in page['entries']:
#                
#                     print ('Ad group with name \'%s\', id \'%s\' and status \'%s\' was '
#                            'found.' % (ad_group['name'], ad_group['id'],
#                                 ad_group['status']))
#           else:
#               print 'No ad groups were found.'
            offset += self.PAGE_SIZE
            selector['paging']['startIndex'] = str(offset)
            try:
                more_pages = offset < int(page['totalNumEntries'])
            except KeyError:
                print "need to check why totalNumEntries is sometimes not getting populated"
                pass
        
        return adgroups
    
    def get_campaign_keywords(self, campaign_id):
        
        # Initialize appropriate service.
        ad_group_criterion_service = self.client.GetAdGroupCriterionService(self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        
        # Construct selector and get all ad group criteria.
        offset = 0
        selector = {
            'fields': ['AdGroupId', 'Id', 'Text', 'KeywordMatchType', 'PlacementUrl'],
            'predicates': [{
                'field': 'CriteriaType',
                'operator': 'EQUALS',
                'values': ['KEYWORD']
            }],
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(self.PAGE_SIZE)
            }
        }
        more_pages = True
        while more_pages:
            page = ad_group_criterion_service.Get(selector)[0]
            
            # Display results.
            if 'entries' in page:
                for criterion in page['entries']:
                    print ('Keyword ad group criterion with ad group id \'%s\', criterion '
                         'id \'%s\', text \'%s\', and match type \'%s\' was found.'
                         % (criterion['adGroupId'], criterion['criterion']['id'],
                            criterion['criterion']['text'],
                            criterion['criterion']['matchType']))
            else:
                print 'No keywords were found.'
            offset += self.PAGE_SIZE
            selector['paging']['startIndex'] = str(offset)
            more_pages = offset < int(page['totalNumEntries'])
            break
        print
        print ('Usage: %s units, %s operations' % (self.client.GetUnits(),
                                                   self.client.GetOperations()))
                                                                                
    pass
    
    
    def get_ad_group_keywords(self, ad_group_id):
        '''
        
        :param ad_group_id:
        '''
        # Initialize appropriate service.
        ad_group_criterion_service = self.client.GetAdGroupCriterionService(
            self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        
        # Construct selector and get all ad group criteria.
        ad_group_keywords = []
        offset = 0
        selector = {
            'fields': ['AdGroupId', 'Id', 'Text', 'KeywordMatchType', 'PlacementUrl'],
            'predicates': [{
                'field': 'CriteriaType',
                'operator': 'EQUALS',
                'values': ['KEYWORD']
            },
                           {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': [str(ad_group_id)]
            },
                           
                           ],
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(self.PAGE_SIZE)
            }
        }
        more_pages = True
        while more_pages:
            page = ad_group_criterion_service.Get(selector)[0]
            
            # Display results.
            if 'entries' in page:
                ad_group_keywords.extend(page['entries'])
            offset += self.PAGE_SIZE
            selector['paging']['startIndex'] = str(offset)
            try:
                more_pages = offset < int(page['totalNumEntries'])
            except KeyError:
                print "need to check why totalNumEntries is sometimes not getting populated"
            
        return ad_group_keywords
    
    def get_ad_group_match_search_queries(self, ad_group_id):
        '''
        Get the Match search queries for a given adgroup
        ToDo: Store in Db for later use
        :param ad_group_id:
        '''
            # Initialize appropriate service.
        ad_group_criterion_service = self.client.GetAdGroupCriterionService(
            self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        
        # Construct selector and get all ad group criteria.
        offset = 0
        selector = {
            'fields': ['searchTerm','AdGroupId', 'Id', 'Text', 'KeywordMatchType', 'PlacementUrl'],
            'predicates': [
                           {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': [ad_group_id]
            },
                           
                           ],
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(self.PAGE_SIZE)
            }
        }
        more_pages = True
        while more_pages:
            page = ad_group_criterion_service.Get(selector)[0]
            # Display results.
            if 'entries' in page:
                for criterion in page['entries']:
                    print ('Keyword ad group criterion with ad group id \'%s\', criterion '
                       'id \'%s\', text \'%s\', and match type \'%s\' was found.'
                       % (criterion['adGroupId'], criterion['criterion']['id'],
                          criterion['criterion']['text'],
                          criterion['criterion']['matchType']))
            else:
                print 'No keywords were found.'
            offset += self.PAGE_SIZE
            selector['paging']['startIndex'] = str(offset)
            more_pages = offset < int(page['totalNumEntries'])
        print
        print ('Usage: %s units, %s operations' % (self.client.GetUnits(),
                                                   self.client.GetOperations()))
    


    def get_all_account_details(self):
        '''
        
        '''
        all_account_details = None
        self.client.use_mcc = True
        # Initialize appropriate service.    
        managed_customer_service = self.client.GetManagedCustomerService(self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        
        # Construct selector to get all accounts.
        selector = {
            'fields': ['Login', 'CustomerId', 'Name']
        }
        # Get serviced account graph.
        graph = managed_customer_service.Get(selector)[0]
        if 'entries' in graph and graph['entries']:
          # Create map from customerId to parent and child links.
          child_links = {}
          parent_links = {}
          if 'links' in graph:
            for link in graph['links']:
              if link['managerCustomerId'] not in child_links:
                child_links[link['managerCustomerId']] = []
              child_links[link['managerCustomerId']].append(link)
              if link['clientCustomerId'] not in parent_links:
                parent_links[link['clientCustomerId']] = []
              parent_links[link['clientCustomerId']].append(link)
          # Create map from customerID to account and find root account.
          accounts = {}
          root_account = None
          for account in graph['entries']:
            accounts[account['customerId']] = account
            if account['customerId'] not in parent_links:
              root_account = account
          # Display account tree.
          if root_account:
              all_account_details = self.get_account_tree(root_account, None, accounts, child_links, 0)
        return all_account_details
    def get_account_tree(self,account, link, accounts, links, depth=0):
        """Displays an account tree.
        
        Args:
          account: dict The account to display.
          link: dict The link used to reach this account.
          accounts: dict Map from customerId to account.
          links: dict Map from customerId to child links.
          depth: int Depth of the current account in the tree.
        """
        all_accounts = []
        all_accounts.append({ 'depth' : depth,
                             "login" : account['login'],
                             'customerId' : account['customerId'],
                             'name' : account['name'],
                             })
        if account['customerId'] in links:
            for child_link in links[account['customerId']]:
                child_account = accounts[child_link['clientCustomerId']]
                accounts_in_subtree = self.get_account_tree(child_account, child_link, accounts, links, depth + 1)
                for temp_account in accounts_in_subtree:
                    all_accounts.append(temp_account)
        return all_accounts
    
    ##################                 
    def add_keywords_to_adgroup(self,keywords):
        # Initialize appropriate service.
        ad_group_criterion_service = self.client.GetAdGroupCriterionService(self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        operations = []
        for temp_kw in keywords:
            # Construct keyword ad group criterion object.
            kw_to_add = {
                'xsi_type': temp_kw.get('keyword_type'),
                'adGroupId': str(temp_kw.get('adgroup_id')),
                'criterion': {
                    'xsi_type': 'Keyword',
                    'matchType': temp_kw.get('match_type'),
                    'text': temp_kw.get('text')
                },
                # These fields are optional.
    #            'userStatus': 'PAUSED',
    #            'destinationUrl': 'http://example.com/mars'
            }
            
            # Construct operations and add ad group criteria.
            operations.append(
                {
                    'operator': 'ADD',
                    'operand': kw_to_add
                },
            )
        # after getting all the operations run it one shot
        ad_group_criteria = ad_group_criterion_service.Mutate(operations)[0]['value']
        # Display results.
        for criterion in ad_group_criteria:
            print ('Keyword ad group criterion with ad group id \'%s\', criterion id '
                 '\'%s\', text \'%s\', and match type \'%s\' was added.'
                 % (criterion['adGroupId'], criterion['criterion']['id'],
                    criterion['criterion']['text'],
                    criterion['criterion']['matchType']))

        pass
    
    def add_keywords_to_campaign(self, keywords):
        # Initialize appropriate service.
        campaign_criterion_service = self.client.GetCampaignCriterionService(self.ADWORDS_URL, self.ADWORDS_API_VERSION)
        operations = []
        for temp_kw in keywords:
            # Construct keyword ad group criterion object.
            kw_to_add = {
#                'xsi_type': KEYWORD_TYPE_NEGATIVE, # For campaign we can just add negative keywords but not a positiive keywords :)
                'campaignId': str(temp_kw.get("campaign_id")),
                'criterion': {
                                'xsi_type': 'Keyword',
                                'matchType': temp_kw.get('match_type') ,
                                'text': temp_kw.get('text')
                },
            }
            
            # Construct operations and add ad group criteria.
            operations.append(
                {
                    'operator': 'ADD',
                    'operand': kw_to_add
                },
            )
        # after getting all the operations run it one shot
        campaign_criteria = campaign_criterion_service.Mutate(operations)[0]['value']
        # Display results.
        for criterion in campaign_criteria:
            print ('Keyword ad group criterion with ad group id \'%s\', criterion id '
                 '\'%s\', text \'%s\', and match type \'%s\' was added.'
                 % (criterion['campaignId'], criterion['criterion']['id'],
                    criterion['criterion']['text'],
                    criterion['criterion']['matchType']))

        pass

        pass

class Csv_interactor():
    ROWTYPE_CAMPAIGN = 'campaign'
    ROWTYPE_ADGROUP = 'adgroup'
    ROWTYPE_KEYWORD = 'keyword'
    ROWTYPE_NEGATIVEKEYWORD = 'negativekeyword'
    ROWTYPE_AD = 'ad'


    def stream_lines(self, file):
        file.seek(0)
        while True:
            line = file.readline().lower()
            if not line:
                break
            yield line.replace( '\x00', '' ).replace( '\xff\xfe', '' ).replace('\xd7','/')
    
        
    @transaction.commit_manually
    def load_csv_file(self,csv_file):

        client = Client.objects.get( name = 'ATC' )
        
        header = []
        cur_campaign = None
        cur_adgroup = None
        temp_time = datetime.datetime.now()
        csv_reader = csv.reader( self.stream_lines(csv_file),
                                         dialect = 'excel-tab', delimiter = '\t', quotechar = '|' )
        for linenumber, row in enumerate( csv_reader ):
            try:
                if linenumber % 10000 == 0 :
                    #endtime = datetime.datetime.now()
                    #print endtime - sttime
                    print "="*70,"timetaken:",datetime.datetime.now()-temp_time,"lno",linenumber
                    temp_time = datetime.datetime.now()
                    transaction.commit()
            
                if row:
                    if linenumber == 0:
                        # headers store them for post processing
                        header = row
                    else:
                        cur_row_type = self._get_row_type( row, header )
                        print cur_row_type
                        if  cur_row_type in [ self.ROWTYPE_CAMPAIGN, self.ROWTYPE_ADGROUP, self.ROWTYPE_KEYWORD, self.ROWTYPE_NEGATIVEKEYWORD, self.ROWTYPE_AD ] :
                            try:
                                if not cur_campaign or cur_campaign.name != row[header.index( 'campaign' )]:
                                    cur_campaign = Campaign.objects.get( name = row[header.index( 'campaign' )] , client = client )
                                    if cur_campaign.status != row[header.index( 'campaign status' )]:
                                        cur_campaign.status = row[header.index( 'campaign status' )]
                                        cur_campaign.save()
                                
                                
                            except Campaign.DoesNotExist:
                                cur_campaign = Campaign( client = client,
                                                         name = row[header.index( 'campaign' )],
                                                         status = row[header.index( 'campaign status' )] )
                                cur_campaign.save()
                                transaction.commit()
                            if cur_row_type ==  self.ROWTYPE_CAMPAIGN:
                                if cur_campaign.daily_budget != row[header.index('campaign daily budget')] :
                                    # record change
                                    rc = Record_change(what_changed = "campaign::"+cur_campaign.name, changed_from = cur_campaign.daily_budget, changed_to = row[header.index('campaign daily budget')] )
                                    rc.save() 
                                    # now do the  change :)
                                    cur_campaign.daily_budget = row[header.index('campaign daily budget')]
                                    cur_campaign.save()
                        if  cur_row_type in  [ self.ROWTYPE_ADGROUP, self.ROWTYPE_AD, self.ROWTYPE_KEYWORD, self.ROWTYPE_NEGATIVEKEYWORD, ] :
                            try:
                                if not cur_adgroup or cur_adgroup.name != row[header.index( 'ad group' )]:
                                    cur_adgroup = Adgroup.objects.get( campaign = cur_campaign, name = row[header.index( 'ad group' )] )
                                    is_dirty = False
                                    if cur_row_type == self.ROWTYPE_ADGROUP:
                                        if row[header.index( 'max cpc' )] and cur_adgroup.max_cpc != row[header.index( 'max cpc' )]:
                                            cur_adgroup.max_cpc = "0"+row[header.index( 'max cpc' )]
                                            is_dirty = True
                                        if row[header.index( 'cpa bid' )] and cur_adgroup.cpa_bid != row[header.index( 'cpa bid' )]:
                                                cur_adgroup.cpa_bid = "0"+row[header.index( 'cpa bid' )]
                                                is_dirty = True
                                        if cur_row_type == self.ROWTYPE_ADGROUP:
                                            if row[header.index( 'adgroup status' )] and cur_adgroup.status != row[header.index( 'adgroup status' )]:
                                                cur_adgroup.status = row[header.index( 'adgroup status' )]
                                                is_dirty = True
                                                
                                        if is_dirty:
                                            cur_adgroup.save()
                                                
                            except Adgroup.DoesNotExist:
                                cur_adgroup = Adgroup( campaign = cur_campaign,
                                                      name = row[header.index( 'ad group' )],
                                                      max_cpc = "0"+row[header.index( 'max cpc' )],
                                                      )
                                if cur_row_type == self.ROWTYPE_ADGROUP:
                                    cur_adgroup.status =  row[header.index( 'adgroup status' )]
                                cur_adgroup.save()
                                transaction.commit()
                        if  cur_row_type in [ self.ROWTYPE_KEYWORD, self.ROWTYPE_NEGATIVEKEYWORD ]:
    #                        print "\t\t\t\tkeyword", row[header.index( 'max cpc' )], row[header.index( 'Keyword' )]
                            # create keyword
                            try:
                                cur_keyword = Keyword.objects.get( text = row[header.index( 'keyword' )] )
                            except Keyword.DoesNotExist:
                                cur_keyword = Keyword( text = row[header.index( 'keyword' )] )
                                cur_keyword.save()
                            # create/update criterion
    
                            try:
                                cur_criterion = Criterion.objects.get( adgroup = cur_adgroup, keyword = cur_keyword , 
                                                                       type = row[header.index('criterion type')] )
    
    #                            if cur_criterion.firstpage_cpc != row[header.index('first page cpc')] or cur_criterion.topofpage_cpc != row[header.index('top of page cpc')] or cur_criterion.quality_score != row[header.index('quality score')] or cur_criterion.status != row[header.index('status')] or cur_criterion.approval_status != row[header.index('approval status')]:
    #                                if cur_criterion.quality_score != row[header.index('quality score')]:
    #                                    rc = Record_change(what_changed="quality score", 
    #                                                       changed_from = cur_criterion.quality_score, 
    #                                                       changed_to = row[header.index('quality score')])
    #                                    rc.save()
    #                                    
    #                                cur_criterion.firstpage_cpc = "0"+row[header.index('first page cpc')]
    #                                cur_criterion.topofpage_cpc = "0"+row[header.index('top Of page cpc')]
    #                                cur_criterion.quality_score = "0"+row[header.index('quality score')]
    #                                cur_criterion.status = row[header.index('status')]
    #                                cur_criterion.approval_status = row[header.index('approval status')]
    #                                cur_criterion.save()
    
                            except Criterion.DoesNotExist:
                                cur_criterion = Criterion( adgroup = cur_adgroup, keyword = cur_keyword , type = row[header.index('criterion type')] )
                                cur_criterion.firstpage_cpc = "0"+row[header.index('first page cpc')]
                                cur_criterion.topofpage_cpc = "0"+row[header.index('top of page cpc')]
                                cur_criterion.quality_score = "0"+row[header.index('quality score')]
                                cur_criterion.match_type = row[header.index( 'criterion type' )]
                                if cur_row_type == self.ROWTYPE_KEYWORD: 
                                    cur_criterion.status = row[header.index('status')]
                                    cur_criterion.approval_status = row[header.index('approval status')]
                                cur_criterion.save()  
    
                        if cur_row_type == self.ROWTYPE_AD:
                            try: 
                                cur_ad = Ad.objects.get(adgroup = cur_adgroup, 
                                               headline = row[header.index('headline')],
                                               description_line1 = row[header.index('description line 1')], 
                                               description_line2 = row[header.index('description line 2')], 
                                               display_url = row[header.index('display url')] ,
                                               destination_url = row[header.index('destination url')],
                                               )
                                if cur_ad.approval_status != row[header.index('approval status')]:
                                    cur_ad.approval_status = row[header.index('Approval Status')]
                                    cur_ad.save()
    
                            except Ad.DoesNotExist:
                                cur_ad = Ad(adgroup = cur_adgroup, 
                                               headline = row[header.index('headline')],
                                               description_line1 = row[header.index('description line 1')], 
                                               description_line2 = row[header.index('description line 2')], 
                                               display_url = row[header.index('display url')] ,
                                               destination_url = row[header.index('destination url')],
                                               )
                                if cur_row_type == self.ROWTYPE_AD:
                                    cur_ad.approval_status = row[header.index('approval status')]
                                cur_ad.save()
    
                                pass
    
                        if not cur_row_type:
                            if row[header.index('order')] or row[header.index('id')] or row[header.index('company_name')]:
                                continue
                            print datetime.datetime.now(), linenumber, row
            except Exception as e:
                print "error::",e,":header::", header,":row::", row
                
        transaction.commit()
        csv_file.close()

    def _get_value( self, row, header, field_name ):
        return row[header.index( field_name )]

    def _get_row_type( self, cur_row, header ):
        if len(cur_row) < 43:
            return self.ROWTYPE_NEGATIVEKEYWORD
    
        if cur_row[header.index( 'campaign daily budget' )] :
            return self.ROWTYPE_CAMPAIGN
        elif cur_row[header.index( 'keyword' )]:
            return self.ROWTYPE_KEYWORD
        elif (cur_row[header.index( 'max cpc' )] or cur_row[header.index( 'cpa bid' )] ) and not cur_row[header.index( 'keyword' )]:
            return self.ROWTYPE_ADGROUP
        elif cur_row[header.index( 'headline' )] and cur_row[header.index( 'description line 1' )]:
            return self.ROWTYPE_AD
        return None



