from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'omero_user_apps.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^omero_signup/', include('omero_signup.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
