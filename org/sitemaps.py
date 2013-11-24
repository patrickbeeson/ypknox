from django.contrib.sitemaps import Sitemap
from ypknox.apps.news.models import PressRelease
from ypknox.apps.events.models import Event
import datetime

class NewsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return PressRelease.live.all()

	def lastmod(self, obj):
		return obj.pub_date

	def location(self, obj):
		return "/news/%s" % obj.slug

class EventsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Event.current.all()

	def lastmod(self, obj):
		return obj.event_date

	def location(self, obj):
		return "/events/%s" % obj.slug