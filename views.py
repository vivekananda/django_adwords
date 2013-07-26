# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import adwords_utils
from json import dumps
from models import Client
from django_adwords.models import Campaign
from django_adwords.forms import DocumentUploadForm
from django.contrib.admin.views.decorators import staff_member_required
import zipfile
from django_adwords.adwords_utils import Csv_interactor 
from django_adwords.models import Data_dump
import os
from subprocess import call

def __load_data_using_mysql_dump(csv_file):
    fName = "atc_adwords_snapshot.csv"
    fd = open( "/tmp/"+fName, "w" )
    fd.write( csv_file.read())
    fd.close()
    call('iconv -f UTF-16 -t UTF-8 /tmp/%s > /var/lib/mysql/sema/%s'% (fName, fName), shell=True)
    import settings
    temp_dict = { 'user': settings.DATABASES['default']['USER'],
                 'host': settings.DATABASES['default']['HOST'],
                 'password': settings.DATABASES['default']['PASSWORD'],
                 'db': settings.DATABASES['default']['NAME'],
                 'filename': fName
                 }
    call('''mysql %(db)s -u %(user)s -p%(password)s -e "LOAD DATA INFILE '%(filename)s' into table django_adwords_data_dump ignore 1 lines ( Campaign , Campaign_Daily_Budget , Languages , Campaign_Id , Location , Ad_Schedule , Networks , Ad_Group , Max_CPC , Display_Network_Max_CPC , Max_CPM , CPA_Bid , Max_CPC_Multiplier , Display_Network_Max_CPC_Multiplier , Max_CPM_Multiplier , Flexible_Reach , Keyword , Criterion_Type , First_Page_CPC , Top_Of_Page_CPC , Quality_Score , Headline , Description_Line_1 , Description_Line_2 , COMPANY_NAME , PHONE_NUMBER , ADDRESS_LINE_1 , ADDRESS_LINE_2 , CITY , STATE , POSTAL_CODE , COUNTRY_CODE , map_icon , Source , Link_Text , Order1 , Display_URL , Destination_URL , Campaign_Status , AdGroup_Status , Status , Approval_Status , Suggested_Changes , Comment) set created = now(), updated=now();"'''% temp_dict , shell=True)
    # Process loaded data
    # identify new campaigns
    call('''mysql %(db)s -u %(user)s -p%(password)s -e "insert into django_adwords_campaign (name, client_id, status) select distinct(Campaign),'1',Campaign_Status  from django_adwords_data_dump  where Keyword='' and Ad_Group='' and created > TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1 day)) and Campaign not in (select distinct(name) from django_adwords_campaign)"'''% temp_dict , shell=True)
    # identify new adgroups
    call('''mysql %(db)s -u %(user)s -p%(password)s -e "insert into django_adwords_adgroup (name, status, campaign_id) select distinct(da_dd.Ad_Group),da_dd.AdGroup_Status, da_c.id from django_adwords_data_dump da_dd, django_adwords_campaign da_c where da_dd.Campaign = da_c.name and da_dd.Keyword='' and da_dd.created > TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1 day)) and da_dd.Ad_Group not in (select distinct(name) from django_adwords_adgroup);"'''% temp_dict , shell=True)
    # identify new keywords
    call('''mysql %(db)s -u %(user)s -p%(password)s -e "insert into django_adwords_keyword (text,status) select distinct(da_dd.Keyword),da_dd.Status from django_adwords_data_dump da_dd where da_dd.Keyword!='' and da_dd.created > TIMESTAMP(DATE_SUB(NOW(), INTERVAL1 day)) and da_dd.Keyword not in (select distinct(text) from django_adwords_keyword);"'''% temp_dict , shell=True)
    # delete or remove paused adgroups
    # Pause all Paused adgroups
    call('''mysql %(db)s -u %(user)s -p%(password)s -e "update django_adwords_adgroup set AdGroup_Status='Paused' from django_adwords_data_dump da_dd, django_adwords_campaign da_c, django_adwords_adgroup da_ag where da_ag.name=da_dd.Ad_Group and da_ag.campaign_id=da_c.id and da_dd.Campaign = da_c.name and da_dd.Keyword='' and da_dd.AdGroup_Status='Paused' and da_dd.created > TIMESTAMP(DATE_SUB(NOW(), INTERVAL 100 day));"'''% temp_dict , shell=True)
    # Mark as delete all the deleted adgroups 
    call('''mysql %(db)s -u %(user)s -p%(password)s -e "update django_adwords_adgroup da_ag set da_ag.status='deleted' where (da_ag.name,da_ag.campaign_id) not in( select distinct da_dd.Ad_Group,da_c.id from django_adwords_data_dump da_dd, django_adwords_campaign da_c where   da_dd.Campaign = da_c.name and da_dd.Keyword='' and da_dd.created > TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1 day)) ) ;"'''% temp_dict , shell=True)
    
@staff_member_required
def load_data_from_file( request ):
    '''
    Export complete account in adword editor and upload it here, 
    This function will parse the file identifies campaigns, adgroups, ads and keywords and populate respective tables.
    
    You can also upload a ziped file 
    (This will be useful to reduce the upload time in case if the server is running in different subnet than your desktop from which you are uploading the file.)
    Also handeled multiple csv files in a zipped archive

    :param request:
    '''
    if request.method == "POST":
        form = DocumentUploadForm( data = request.POST, files = request.FILES )
        if form.is_valid():
            ci = Csv_interactor()
            uploaded_file = request.FILES["csvfile"]
            #save uploadedfile in /tmp
            temp_fd = open( os.path.join("/tmp", uploaded_file.name), "wb+" )
            for chunk in uploaded_file.chunks():
                temp_fd.write(chunk)
            temp_fd.close()
            csv_file = open( os.path.join("/tmp", uploaded_file.name), "r" )
            
            if uploaded_file.name.endswith( ".zip" ):
                zfile = zipfile.ZipFile( csv_file )
                for name in zfile.namelist():
                    __load_data_using_mysql_dump(zfile.open(name))
            else:
                __load_data_using_mysql_dump(csv_file)
            csv_file.close()
            return render_to_response( 'django_adwords/upload.html', {'form': form, 'msg':'File successfully uploaded,'},
                              context_instance = RequestContext( request ) )
    else:
        form = DocumentUploadForm() # A empty, unbound form
        # Render list page with the documents and the form
    return render_to_response( 'django_adwords/upload.html', {'form': form, 'msg':'upload the zipped csv file you got by exporting account from adwords editor'},
                              context_instance = RequestContext( request ) )

def load_keyword_data( request ):
    pass
def get_and_store( request, action = None, val = None ):
    '''
    Triggeres specific API calls to fetch and pupulate Accounts and Campaigns in those accounts
    Use this to populate initial data
    :param request:
    :param action: get_all_account_details, get_all_campaigns 
    :param val: Account 
    '''
    result = {'r':'failed'}
    result['action'] = action
    ai = adwords_utils.Adwords_interactor()

    if action == 'get_all_account_details':
        all_client_details = ai.get_all_account_details()
        for temp_client in all_client_details:
            print temp_client['customerId']
            import pdb; pdb.set_trace()
            try:
                c = Client.objects.get( login = temp_client['login'])
                if c.client_id != temp_client['customerId']:
                    c.client_id = temp_client['customerId']
                    c.name = temp_client['name']
                    c.save()
            except Client.DoesNotExist:
                c = Client( client_id = temp_client['customerId'], name = temp_client['name'], login = temp_client['login'], depth = temp_client['depth'] )
                c.save()
        result['d'] = all_client_details
        result['r'] = 'success'

    elif action == 'get_all_campaigns':
        """
        get all campaigns data
        """
        try:
            temp_client = Client.objects.get( id = val )

            all_campaigns = ai.get_all_campaigns( temp_client.id )
            for temp_campaign in all_campaigns:
                try:
                    c = Campaign.objects.get( name = temp_campaign['name'] )
                    if not c.id:
                        c.id = temp_campaign['id']
                        c.save()
                except Campaign.DoesNotExist: 
                    c = Campaign( client = temp_client,
                                 id = temp_campaign['id'],
                                 name = temp_campaign['name'],
                                 status = temp_campaign['status'],
                                 campaign_stats = temp_campaign['campaignStats'],
                                 frequency_cap = temp_campaign['frequencyCap'],
                                 )
                    c.save()
            result['d'] = all_campaigns
            result['r'] = 'success'

        except Client.DoesNotExist:
            result['d'] = "client doesn't exist"
    elif action == 'gat_':
        pass
    else:
        pass
    return HttpResponse( dumps( result ) )

def index( request ):

    url_data = [{'action':'get_all_account_details', 'name':'', 'val':None} ]
    clients = Client.objects.all()
    for temp_client in clients:
        url_data.append( {'action':"get_all_campaigns", 'name':temp_client.name, 'val':temp_client.id} )
    return render_to_response( 'django_adwords/index.html', {'url_data': url_data }, context_instance = RequestContext( request ) )


def check_for_new_campaigns_adgroups_keywords(request):
    return HttpResponse("ToDo: Better use the bulk uploader and upload the entire account to minimize cost:")