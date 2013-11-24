import datetime, time

from django.forms import ModelForm

from django.views.generic import list_detail, date_based
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from ypknox.apps.events.models import Attendee, Event

class RSVPForm(ModelForm):
	class Meta:
		model = Attendee
		exclude = ('created', 'updated', 'event', 'user',)

def event_list(request, page=0):
	return list_detail.object_list(
		request,
		queryset = Event.current.all().order_by('event_date'),
		paginate_by = 20,
		page = page,
		template_name = 'events/event_archive.html',
	)

def event_detail(request, slug, year, month, day, form_class=RSVPForm):
	if request.user.is_authenticated():
		try:
			date = datetime.date(*time.strptime(\
										year+month+day,
										'%Y%b%d')[:3])
		except ValueError:
			raise Http404
	
		try:
			event = Event.objects.get(slug=slug, event_date=date)
		except Attendee.DoesNotExist:
			raise Http404	
	
		try:
			rsvp = Attendee.objects.get(user=request.user, event=event)
		except Attendee.DoesNotExist:
			rsvp = None
	
		if request.method == 'POST':
			form = RSVPForm(data=request.POST, instance=rsvp)
		
			if form.is_valid():
				try:
					date = datetime.date(*time.strptime(\
										year+month+day,
										'%Y%b%d')[:3])
				except ValueError:
					raise Http404

				attendee = form.save(commit=False)
				attendee.event = Event.objects.get(slug=slug, event_date=date)
				attendee.user = request.user
				attendee.save()
				return HttpResponseRedirect(reverse('ypknox.apps.events.views.event_thanks', args=(event.id, attendee.id)))
		else:
			form = RSVPForm(instance=rsvp)

		return date_based.object_detail(
			request,
			date_field = 'event_date',
			year = year,
			month = month,
			day = day,
			queryset = Event.objects.all(),
			allow_future = True,
			template_name = 'events/event_detail.html',
			slug = slug,
			extra_context = {'form': form}
		)
	else:
		return date_based.object_detail(
			request,
			date_field = 'event_date',
			year = year,
			month = month,
			day = day,
			queryset = Event.objects.all(),
			allow_future = True,
			template_name = 'events/event_detail.html',
			slug = slug,
		)

def event_thanks(request, event_id, attendee_id):
    e = get_object_or_404(Event, pk=event_id)
    a = get_object_or_404(Attendee, pk=attendee_id)
    return render_to_response('events/thanks.html', {'event': e, 'attendee': a,})