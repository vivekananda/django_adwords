from django.contrib import admin
from django_adwords.models import Client, Campaign, Adgroup, Keyword, Criterion,\
    Record_change, Ad
from django_adwords.adwords_utils import Adwords_interactor

admin.site.register(Client)

def get_adgroups( modeladmin, request, queryset ):
    ai = Adwords_interactor()
    for temp_campaign in queryset:
        adgroups_of_campaign = ai.get_ad_groups( campaign_id = temp_campaign.id )
        for temp_adgroup in adgroups_of_campaign:
            try:
                Adgroup.objects.get( id = temp_adgroup['id'] )
            except Adgroup.DoesNotExist:
                ag = Adgroup( 
                             campaign = temp_campaign,
                             campaign_id = temp_adgroup['id'],
                             name = temp_adgroup['name'],
                             status = temp_adgroup['status'],
                             stats = temp_adgroup['stats']
                             )
                ag.save()

get_adgroups.short_description = "Fetch Adgroups from GA"

class CampaignAdmin(admin.ModelAdmin):
#    fields = ['id','name','client','status']
    list_display = ('campaign_id','name','client','status','updated','created') 
    list_filter = ['status','client']
    search_fields = ['name']
    date_hierarchy = 'updated'
    actions = [get_adgroups]

admin.site.register(Campaign,CampaignAdmin)


def get_keywords(modeladmin, request, queryset):
    ai = Adwords_interactor()
    for temp_adgroup in queryset:
        adgroup_keywords = ai.get_ad_group_keywords( ad_group_id = temp_adgroup.id )
        for temp_keyword in adgroup_keywords:
            try:
                Keyword.objects.get(id=temp_keyword['criterion']['id'])
            except Keyword.DoesNotExist:
                kw = Keyword(
                                adgroup = temp_adgroup,
                                id = temp_keyword['criterion']['id'],
                                text = temp_keyword['criterion']['text'],
                                type = temp_keyword['criterion']['type'], 
                                match_type = temp_keyword['criterion']['matchType'],
                                stats = temp_keyword.get('stats',0),
                                adgroupcriterion_type = temp_keyword['AdGroupCriterion_Type'],
                                criterion_use = temp_keyword['criterionUse'],
                                criterion_type = temp_keyword['criterion']['type'],
                             )
                kw.save() 

get_keywords.short_description = "Fetch Keywords from GA"

class AdgroupAdmin(admin.ModelAdmin):
    list_display = ('adgroup_id','name','campaign','status','updated','created') 
    list_filter = ['status','campaign']
    search_fields = ['name']
    date_hierarchy = 'updated'
    actions = [get_keywords]

admin.site.register(Adgroup,AdgroupAdmin)

class KeywordAdmin(admin.ModelAdmin):
    list_display = ('text','status','updated','created') 
    list_filter = ['status']
    search_fields = ['text']
    date_hierarchy = 'updated'

admin.site.register(Keyword, KeywordAdmin)

admin.site.register(Criterion)
admin.site.register(Record_change)
admin.site.register(Ad)

