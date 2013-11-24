from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import list_detail, date_based
from django.views.generic.simple import direct_to_template
from django.contrib.sitemaps import FlatPageSitemap
from django.contrib import databrowse
from django.contrib.auth.decorators import login_required 

from ypknox.apps.events.models import Event, Location, Attendee
from ypknox.apps.category.models import Category
from ypknox.apps.links.models import Link
from ypknox.apps.news.models import PressRelease
from ypknox import views
from ypknox.feeds import LatestNewsFeed, UpcomingEventsFeed
from ypknox.sitemaps import NewsSitemap, EventsSitemap
from ypknox.apps.events import views

admin.autodiscover()

# Functions for passing into extra context
def get_live_pressreleases():
	return PressRelease.live.all()

def get_current_events():
	return Event.current.all()

# Category dicts
category_list_info_dict = {
	'queryset': Category.objects.all(),
	'allow_empty': True,
}

category_detail_info_dict = {
	'queryset': Category.objects.all(),
	'extra_context' : {'event_list': get_current_events, 'pressrelease_list': get_live_pressreleases},
	'template_object_name': 'category',
}

# Link dict
link_list_info_dict = {
	'queryset': Link.objects.all(),
	'allow_empty': True,
}

# Location dicts
location_list_info_dict = {
	'queryset': Location.objects.all(),
	'extra_context': {'event_list': get_current_events},
	'allow_empty': True,
}

location_detail_info_dict = {
	'queryset': Location.objects.all(),
	'extra_context': {'event_list': get_current_events},
	'template_object_name': 'location',
}

# Event dict
event_info_dict = {
	'queryset': Event.current.all().order_by('event_date'),
	'date_field': 'event_date',
	'allow_future': True,
}

event_detail_info_dict = {
	'queryset': Event.objects.all(),
	'date_field': 'event_date',
	'allow_future': True,
}

# News dict
news_info_dict = {
	'queryset': PressRelease.live.all(),
	'date_field': 'pub_date',
}

news_list_info_dict = {
	'queryset': PressRelease.live.all().order_by('-pub_date'),
	'paginate_by': 15,
}

# Feeds
feeds = {
	'news': LatestNewsFeed,
	'events': UpcomingEventsFeed,
}

# Sitemaps
sitemaps = {
	'news': NewsSitemap,
	'events': EventsSitemap,
    'flatpages': FlatPageSitemap,
}

urlpatterns = patterns('',

	# Category
	(r'^categories/$', list_detail.object_list, category_list_info_dict),
	(r'^categories/(?P<slug>[-\w]+)/$', list_detail.object_detail, category_detail_info_dict),
	
	# Links
	(r'^links/$', list_detail.object_list, link_list_info_dict),
	
	# Events
	#(r'^events/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$', date_based.object_detail, dict(event_detail_info_dict, slug_field='slug')),
	(r'^events/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$', 'ypknox.apps.events.views.event_detail'),
	(r'^events/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', date_based.archive_day, event_info_dict),
	(r'^events/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', date_based.archive_month, event_info_dict),
	(r'^events/(?P<year>\d{4})/$', date_based.archive_year, dict(event_info_dict, make_object_list=True)),
	#(r'^events/$', date_based.archive_index, event_info_dict), Not using because old events were showing up in archive PB
	(r'^events/$', 'ypknox.apps.events.views.event_list'),
	
	# Locations
	(r'^locations/$', list_detail.object_list, location_list_info_dict),
	(r'^locations/(?P<slug>[-\w]+)/$', list_detail.object_detail, location_detail_info_dict),
	
	# News
	(r'^news/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$', date_based.object_detail, dict(news_info_dict, slug_field='slug')),
	(r'^news/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', date_based.archive_day, news_info_dict),
	(r'^news/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', date_based.archive_month, news_info_dict),
	(r'^news/(?P<year>\d{4})/$', date_based.archive_year, dict(news_info_dict, make_object_list=True)),
	(r'^news/$', list_detail.object_list, news_list_info_dict),
	
	# Contact form
	(r'^contact/', include('contact_form.urls')),
	
	# Homepage
	(r'^$', 'ypknox.views.home_page'),
	
	# Feeds
	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', { 'feed_dict': feeds }),

	# Sitemaps
	(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
	(r'^sitemap-(?P<section>.+).xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

	# Accounts
	(r'^accounts/', include('registration.urls')),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	
	# Profiles
	(r'^profiles/', include('profiles.urls')),

	# RSVP
	(r'^events/(?P<event_id>\d+)/(?P<attendee_id>\d+)/thanks/$', 'ypknox.apps.events.views.event_thanks'),

	# Databrowse
	(r'^databrowse/(.*)', login_required(databrowse.site.root)),
	
	# APIbuilder
	(r'^api/',include('apibuilder.urls')),

	# Admin
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	('^admin/(.*)', admin.site.root),
	(r'^tiny_mce/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': '/home/ypknox/webapps/media/tinymce/jscripts/tiny_mce'}, ),
	
	# Flatpages
	(r'', include('django.contrib.flatpages.urls')),
)
