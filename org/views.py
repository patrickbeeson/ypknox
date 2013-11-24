from django.views.generic.simple import direct_to_template
from ypknox.apps.events.models import Event
from ypknox.apps.news.models import PressRelease

def home_page(request):
	return direct_to_template(
		request,
		extra_context={'event_list': Event.current.all().order_by('event_date')[:4], 'pressrelease_list': PressRelease.live.all().order_by('-pub_date')[:5]},
		template = 'home.html',
	)
