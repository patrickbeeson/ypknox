from django.db import models
import datetime
from ypknox.apps.category.models import Category
from ypknox.apps.media.models import Photo
from markdown import markdown
from django.contrib.sitemaps import ping_google
from django.contrib.localflavor.us.models import *
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.template import loader, Context
from django.conf import settings
from django.contrib.sites.models import Site

class CurrentManager(models.Manager):
	def get_query_set(self):
		return super(CurrentManager, self).get_query_set().filter(event_date__gte=datetime.date.today())

class Event(models.Model):
	CASUAL = 1
	FORMAL = 2
	BUSINESS_CASUAL = 3
	ATTIRE_CHOICES = (
		(CASUAL, 'Casual'),
		(FORMAL, 'Formal'),
		(BUSINESS_CASUAL, 'Business casual'),
	)
	MEMBERS = 4
	GENERAL_PUBLIC = 5
	AUDIENCE_CHOICES = (
		(MEMBERS, 'Members'),
		(GENERAL_PUBLIC, 'General public'),
	)
	pub_date = models.DateTimeField(default=datetime.datetime.now, editable=False, auto_now_add=True)
	slug = models.SlugField(unique=True, help_text='This field will prepopulate from the name field.')
	name = models.CharField(max_length=200)
	event_leader = models.ForeignKey(User, null=True, limit_choices_to = {'groups': 1},)
	location = models.ForeignKey('Location')
	description = models.TextField(help_text='Please use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown syntax</a>.')
	description_html = models.TextField(editable=False, blank=True)
	event_date = models.DateField()
	start_time = models.TimeField()
	finish_time = models.TimeField()
	rsvp = models.BooleanField(blank=True, null=True, default=False, help_text='Check this if the event requires an RSVP.')
	payments_accepted = models.BooleanField(blank=True, null=True, default=False, help_text='Check this if you wish to accept payment for this event.')
	audience = models.IntegerField(choices=AUDIENCE_CHOICES, default=GENERAL_PUBLIC, help_text='Chose the audience intended for this event.')
	attire = models.IntegerField(choices=ATTIRE_CHOICES, default=CASUAL)
	category = models.ForeignKey(Category)
	lead_photo = models.ForeignKey(Photo, null=True, blank=True, help_text='Photo will be resized on the template.')
	keywords = models.CharField(max_length=200, blank=True, help_text='Enter a comma-separated list of keywords.')
	objects = models.Manager()
	current = CurrentManager()

	class Meta:
		verbose_name_plural = 'events'
	
	def __unicode__(self):
		return self.name

	def save(self):
		self.description_html = markdown(self.description)
		super(Event, self).save()
		try:
			ping_google()
		except Exception:
			pass

	def get_absolute_url(self):
		return "/events/%s/%s/" % (self.event_date.strftime("%Y/%b/%d").lower(), self.slug)
		
	def is_expired(self):
		"""Returns True if the event's date is less than the current date."""
		return self.event_date < datetime.date.today()

	def attendees_attending(self):
		"""Returns True if the event's date is less than the current date."""
		return self.attendees.filter(attending_status=1)
	
	def attendees_not_attending(self):
		"""Returns True if the event's date is less than the current date."""
		return self.attendees.filter(attending_status=2)
	
	def attendees_may_attend(self):
		"""Returns True if the event's date is less than the current date."""
		return self.attendees.filter(attending_status=3)
	
	def attendees_no_rsvp(self):
		"""Returns guest"""
		return self.attendees.filter(attending_status=4)
		
	def expected_attendence(self):
		"""Returns number of those attending the event."""
		return self.attendees.all().filter(attending_status=1).count()

class Attendee(models.Model):
	YES = 1
	NO = 2
	MAYBE = 3
	NO_RSVP = 4
	ATTENDING_CHOICES = (
		(YES, 'Yes'),
		(NO, 'No'),
		(MAYBE, 'Maybe'),
		(NO_RSVP, 'Haven\'t RSVPed yet')
	)
	event = models.ForeignKey(Event, related_name='attendees')
	user = models.ForeignKey(User)
	attending_status = models.SmallIntegerField(choices=ATTENDING_CHOICES, default=4)
	number_of_guests = models.SmallIntegerField(default=0, help_text='Indicate the number of guests you expect to accompany you.')
	comment = models.TextField(blank=True, help_text='Leave a comment for the event leader.')
	created = models.DateTimeField(default=datetime.datetime.now)
	updated = models.DateTimeField(blank=True, null=True)
	
	def __unicode__(self):
		return u"%s - %s" % (self.event.name, self.user.get_full_name())
	
	def save(self):
		self.updated = datetime.datetime.now()
		super(Attendee, self).save()

class FeaturedEvent(models.Model):
	live_date = models.DateTimeField(default=datetime.datetime.now)
	name = models.CharField(max_length=200)
	event_to_feature = models.ForeignKey(Event, help_text='Select the event you wish to make a featured event. Only one event can be featured at a time.')
	featured_event_photo = models.ForeignKey(Photo, null=True, help_text='Featured photo needs to be 573 pixels wide and 180 pixels tall.')
	
	class Meta:
		verbose_name_plural = 'featured events'

	def __unicode__(self):
		return self.name

class Location(models.Model):
	slug = models.SlugField(help_text='This field will prepopulate from the name field.', unique=True)
	name = models.CharField(max_length=200)
	prename = models.CharField(max_length=200, help_text='Use this field if there are multiple instances for this location. For example, Aubrey\'s Papermill and Aubrey\'s Middlebrook Pike.', blank=True)
	description = models.TextField(help_text='Please use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown syntax</a>.')
	description_html = models.TextField(editable=False, blank=True)
	street_address = models.CharField(max_length=200, blank=True)
	city = models.CharField(max_length=200)
	zip_code = models.IntegerField()
	state = USStateField()
	phone_number = PhoneNumberField(blank=True)
	web_site = models.URLField(blank=True)
	google_map_link = models.URLField(blank=True, help_text='Copy and paste the link to the <a href="http://google.com/maps">Google map</a> for this location.')
		
	class Meta:
		verbose_name_plural = 'locations'
	
	def __unicode__(self):
		if self.prename:
			return '%s %s' % (self.name, self.prename)
		else:
			return self.name

	def save(self):
		self.description_html = markdown(self.description)
		super(Location, self).save()

	def get_absolute_url(self):
		return '/locations/%s/' % (self.slug)

	def full_name(self):
		"""
		Returns the full name of the location.
		"""
		if self.prename:
			return '%s %s' % (self.name, self.prename)
		else:
			return self.name
			
	def current_event_set(self):
		"""
		Returns current events for a location.
		"""
		return self.event_set.filter(event_date__gte=datetime.date.today())