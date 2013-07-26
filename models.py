from django.db import models
import datetime

CRITERION_TYPE_ADGROUP_POSITIVE = 'Adgroup Positive'
CRITERION_TYPE_ADGROUP_NEGATIVE = 'Adgroup Negative'

# Create your models here.

class Client( models.Model ):
    client_id = models.BigIntegerField( blank = True, null = True )
    name = models.CharField( max_length = 100, db_index=True)
    login = models.CharField( max_length = 100 )
    depth = models.IntegerField( default = 0 )

    def __unicode__( self ):
        return self.name

class Campaign( models.Model ):
    client = models.ForeignKey( Client )
    campaign_id = models.IntegerField( blank = True, null = True )

    name = models.CharField( max_length = 100, db_index=True )
    status = models.CharField( max_length = 10 )
    campaign_stats = models.CharField( max_length = 500, blank = True, null = True  )
    frequency_cap = models.CharField( max_length = 500, blank = True, null = True  )
    daily_budget = models.FloatField( default = 0 )
    created = models.DateTimeField( auto_now_add = True )
    updated = models.DateTimeField( auto_now = True )

    def __unicode__( self ):
        return self.name

class Adgroup( models.Model ):
    campaign = models.ForeignKey( Campaign )
    adgroup_id = models.IntegerField( blank = True, null = True )
    name = models.CharField( max_length = 100, db_index=True )
    max_cpc = models.FloatField( default = 0 )
    cpa_bid = models.FloatField( default = 0 )
    status = models.CharField( max_length = 100 )
    stats = models.CharField( max_length = 500 )

    created = models.DateTimeField( auto_now_add = True )
    updated = models.DateTimeField( auto_now = True )

    def __unicode__( self ):
        return self.name

class Keyword( models.Model ):
    keyword_id = models.IntegerField( blank = True, null = True )
    text = models.CharField( max_length = 100 , db_index=True)

    status = models.CharField( max_length = 10 , blank = True , null = True )
    stats = models.CharField( max_length = 500 )

    created = models.DateTimeField( auto_now_add = True )
    updated = models.DateTimeField( auto_now = True )

    def __unicode__( self ):
        return self.text

class Criterion( models.Model ):
    adgroup = models.ForeignKey( Adgroup , db_index=True)
    keyword = models.ForeignKey( Keyword , db_index=True)
    criterion_id = models.IntegerField( default = 0 )
    type = models.CharField( max_length = 100, blank = True , null = True , db_index=True)
    firstpage_cpc = models.FloatField( default = 0 )
    topofpage_cpc = models.FloatField( default = 0 )
    quality_score = models.FloatField( default = 0 )

    match_type = models.CharField( max_length = 100 , blank = True , null = True )
    status = models.CharField( max_length = 10 , blank = True , null = True )
    stats = models.CharField( max_length = 500 , blank = True , null = True )

    adgroupcriterion_type = models.CharField( max_length = 100, blank = True , null = True )
    criterion_use = models.CharField( max_length = 100, blank = True , null = True )
    criterion_type = models.CharField( max_length = 100, blank = True , null = True )

    created = models.DateTimeField( auto_now_add = True )
    updated = models.DateTimeField( auto_now = True )

    def __unicode__( self ):
        return self.match_type

class Ad( models.Model ):
    adgroup = models.ForeignKey( Adgroup )
    headline = models.CharField( max_length = 200 , db_index=True)
    description_line1 = models.CharField( max_length = 500, db_index=True )
    description_line2 = models.CharField( max_length = 500, db_index=True )

    display_url = models.CharField( max_length = 200, db_index=True )
    destination_url = models.CharField( max_length = 500, db_index=True )
    approval_status = models.CharField( max_length = 20 )

    created = models.DateTimeField( auto_now_add = True )
    updated = models.DateTimeField( auto_now = True )

    def __unicode__( self ):
        return self.headline


class Record_change( models.Model ):
    what_changed = models.CharField( max_length = 100 )
    changed_from = models.CharField( max_length = 100 )
    changed_to = models.CharField( max_length = 100 )

    created = models.DateTimeField( auto_now_add = True )
    updated = models.DateTimeField( auto_now = True )

    def __unicode__( self ):
        return "%s:: %s:: %s -> %s " % ( self.updated, self.what_changed, self.changed_from, self.changed_to )


class Data_dump(models.Model):
    Campaign = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Campaign_Daily_Budget = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Languages  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Campaign_Id  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Location  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Ad_Schedule  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Networks  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Ad_Group  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Max_CPC  = models.FloatField() 
    Display_Network_Max_CPC  = models.FloatField() 
    Max_CPM  = models.FloatField() 
    CPA_Bid  = models.FloatField() 
    Max_CPC_Multiplier  = models.FloatField() 
    Display_Network_Max_CPC_Multiplier  = models.FloatField() 
    Max_CPM_Multiplier  = models.FloatField() 
    Flexible_Reach  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Keyword = models.CharField(max_length=500, null = True, blank = True, db_index = True )
    Criterion_Type  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    First_Page_CPC  = models.FloatField() 
    Top_Of_Page_CPC  = models.FloatField() 
    Quality_Score  = models.FloatField() 
    Headline  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Description_Line_1  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Description_Line_2  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    COMPANY_NAME  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    PHONE_NUMBER  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    ADDRESS_LINE_1  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    ADDRESS_LINE_2  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    CITY  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    STATE  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    POSTAL_CODE  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    COUNTRY_CODE  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    map_icon  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Source  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Link_Text  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Order1 = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Display_URL  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Destination_URL  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Campaign_Status  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    AdGroup_Status  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Status  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Approval_Status  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Suggested_Changes  = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    Comment = models.CharField(max_length=500, null = True, blank = True, db_index = True ) 
    
    created = models.DateTimeField( auto_now_add = True )
    updated = models.DateTimeField( auto_now = True )
    
class Keyword_stats(models.Model):
    Keyword_state = models.CharField(max_length=500, null = True, blank = True) 
    Keyword = models.CharField(max_length=500, null = True, blank = True) 
    Campaign = models.CharField(max_length=500, null = True, blank = True) 
    Ad_group = models.CharField(max_length=500, null = True, blank = True) 
    Status = models.CharField(max_length=500, null = True, blank = True) 
    Max_CPC = models.FloatField() 
    Clicks = models.FloatField() 
    Impressions = models.FloatField() 
    CTR = models.FloatField() 
    Avg_CPC = models.FloatField() 
    Cost = models.FloatField() 
    Avg_position = models.FloatField() 
    Conv_1_per_click = models.FloatField() 
    Cost_By_conv_1_per_click = models.FloatField() 
    Conv_rate_1_per_click = models.FloatField() 
    Quality_score = models.FloatField() 
    Avg_CPM = models.FloatField() 
    View_through_Conv = models.CharField(max_length=500, null = True, blank = True)
    Conv_many_per_click = models.FloatField() 
    CostByConv_many_per_click = models.FloatField() 
    Conv_Rate_many_per_click = models.FloatField() 
    Total_conv_value = models.FloatField() 
    Conv_value_By_cost = models.FloatField() 
    Conv_value_By_click = models.FloatField() 
    Value_By_conv_1_per_click = models.FloatField() 
    Value_By_conv_many_per_click = models.FloatField() 
    Labels = models.CharField(max_length=500, null = True, blank = True)
    Destination_URL = models.CharField(max_length=500, null = True, blank = True)
    First_page_CPC = models.FloatField() 
    Top_of_page_CPC = models.FloatField() 
    Match_type = models.CharField(max_length=500, null = True, blank = True)
    
    for_day = models.DateField( auto_now_add = True )
    last_updated = models.DateTimeField( auto_now = True )
