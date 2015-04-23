from django.conf.urls import *
from omero_signup import views

urlpatterns = patterns('django.views.generic.simple',

    url(r'^requests', views.all_requests, name='omero_signup_requests'),
    url(r'^new/(?P<action>[a-z]+)?$', views.create_request, name='omero_signup_create_request'), 
    url(r'^(?P<action>[a-z]+)/(?:(?P<account_id>[0-9]+)/)?$', views.manage_requests, name='omero_signup_manage_requests'),
    url(r'^change_password/(?P<account_id>[0-9]+)/$', views.manage_password,
        name="omero_signup_changepassword"),  
    url(r'^(?P<account_id>[0-9]+)/delete/$', views.delete_request, name='omero_signup_delete_request'),  
    url(r'^meta',views.display_meta, name='omero_signup_meta'),
 )
