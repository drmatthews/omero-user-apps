from django.conf.urls import *
from omero_graph import views

urlpatterns = patterns('django.views.generic.simple',

    url(r'^$', views.index, name='graphs'),
    url(r'^find', views.index, name='find'),
    url(r'^plot/(?:(?P<annotation_id>[0-999]+)/)$', views.plot, name='plot'),
 )