from django.utils.feedgenerator import Atom1Feed
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from ypknox.apps.news.models import PressRelease
from ypknox.apps.events.models import Event

current_site = Site.objects.get_current()

class LatestNewsFeed(Feed):
	author_name = "Young Professionals of Knoxville"
	copyright = "http://%s/about/" % current_site.domain
	description = "Latest press releases posted to %s" % current_site.name
	feed_type = Atom1Feed
	item_copyright = "http://%s/about/" % current_site.domain
	item_author_name = "casey@ypknox.com"
	link = "/feeds/news/"
	title = "Latest press releases | %s" % current_site.name
	
	def items(self):
		return PressRelease.live.all().order_by('-pub_date')[:15]
	
	def item_pubdate(self, item):
		return item.pub_date
	
	def item_guid(self, item):
		return "tag:%s,%s:%s" % (current_site.domain, item.pub_date.strftime('%Y-%m-%d'), item.get_absolute_url())
	
	def item_category(self, item):
		return item.category

class UpcomingEventsFeed(Feed):
	author_name = "Young Professionals of Knoxville"
	copyright = "http://%s/about/" % current_site.domain
	description = "Upcoming events for %s" % current_site.name
	feed_type = Atom1Feed
	item_copyright = "http://%s/about/" % current_site.domain
	item_author_name = "casey@ypknox.com"
	link = "/feeds/events/"
	title = "Upcoming events | %s" % current_site.name
	
	def items(self):
		return Event.objects.all().order_by('-pub_date')[:15]
	
	def item_pubdate(self, item):
		return item.pub_date
	
	def item_guid(self, item):
		return "tag:%s,%s:%s" % (current_site.domain, item.event_date.strftime('%Y-%m-%d'), item.get_absolute_url())
	
	def item_category(self, item):
		return item.category