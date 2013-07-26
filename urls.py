from django.conf.urls import patterns, url

from django_adwords import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='adwords_home'),
    url(r'^get_and_store/(?P<action>[-\w]+)$', views.get_and_store, name='get_and_store'),
    url(r'^get_and_store/(?P<action>[-\w]+)/(?P<val>[-\w]+)$', views.get_and_store, name='get_and_store'),
    url(r'^load_data_from_file/$', views.load_data_from_file, name='load_data_from_file'),
    url(r'^check_for_new_campaigns_adgroups_keywords/$', views.check_for_new_campaigns_adgroups_keywords, name='check_for_new_campaigns_adgroups_keywords'),
    
)