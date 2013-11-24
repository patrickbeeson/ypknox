from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.localflavor.us.models import *
from django.db.models import permalink

import datetime
from dateutil import relativedelta
import re

from markdown import markdown

class Profile(models.Model):
	user = models.ForeignKey(User, unique=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	bio = models.TextField(help_text='A brief description of yourself. Please use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown syntax</a> if formatting is needed. No HTML is allowed.')
	bio_html = models.TextField(blank=True, editable=False)
	phone_number = PhoneNumberField(help_text='Your phone number in xxx-xxx-xxxx format.')
	birth_date = models.DateField(blank=True, null=True)
	address1 = models.CharField(blank=True, max_length=100)
	address2 = models.CharField(blank=True, max_length=100)
	city = models.CharField(blank=True, max_length=100)
	state = USStateField(blank=True, max_length=100, help_text='or Province')
	zip = models.IntegerField(blank=True, max_length=10)
	personal_website = models.URLField(blank=True)
	mugshot = models.FileField(upload_to='images/photos/users', blank=True, help_text='Please use JPG format and reduce image size to less than 5K.')	
	resume = models.FileField(blank=True, upload_to='documents/users/resumes', help_text='Please use either DOC or PDF format.')
	employer = models.CharField(blank=True, max_length=100)
	employer_website = models.URLField(blank=True)
	linkedin_profile = models.URLField(blank=True, help_text='i.e. http://www.linkedin.com/in/patrickbeeson')
	facebook_profile = models.URLField(blank=True, help_text='i.e. http://www.facebook.com/people/Patrick-Beeson/27403640')
	twitter_profile = models.URLField(blank=True, help_text='i.e. http://twitter.com/patrickbeeson')
	is_public = models.BooleanField(default=True, help_text='By checking this box your profile will be accessible to other YPK members.')
	
	class Meta:
		verbose_name_plural = 'User profiles'
	
	def __unicode__(self):
		return self.user.get_full_name()
	
	@property
	def age(self):
		TODAY = datetime.date.today()
		if self.birth_date:
			return u"%s" % relativedelta.relativedelta(TODAY, self.birth_date).years
		else:
			return None

	def save(self):
		self.bio_html = markdown(self.bio)
		if self.first_name or self.last_name:
			self.user.first_name = self.first_name
			self.user.last_name = self.last_name
			self.user.save()
		super(Profile, self).save()
		
		