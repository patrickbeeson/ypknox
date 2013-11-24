from django.db import models
from ypknox.apps.category.models import Category
from django.contrib.auth.models import User
from ypknox.apps.events.models import Event
from ypknox.apps.media.models import Photo
import datetime
from markdown import markdown
from django.contrib.sitemaps import ping_google

class LiveEntryManager(models.Manager):
    def get_query_set(self):
        return super(LiveEntryManager, self).get_query_set().filter(status=self.model.LIVE_STATUS)

class PressRelease(models.Model):
    LIVE_STATUS = 1
    DRAFT_STATUS = 2
    HIDDEN_STATUS = 3
    STATUS_CHOICES = (
        (LIVE_STATUS, 'Live'),
        (DRAFT_STATUS, 'Draft'),
        (HIDDEN_STATUS, 'Hidden'),
    )
    author = models.ForeignKey(User)
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    slug = models.SlugField(unique_for_date='pub_date', help_text='This field will prepopulate from the headline.')
    headline = models.CharField(max_length=50)
    summary = models.TextField(help_text='Please use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown syntax</a> if needed.')
    summary_html = models.TextField(editable=False, blank=True)
    body = models.TextField(help_text='Please use the WYSIWYG for adding style elements instead of using HTML or CSS. Do not copy and paste from a text editor like Microsoft Word.')
    category = models.ForeignKey(Category)
    related_event = models.ForeignKey(Event, blank=True, null=True, help_text='If this press release is related to an event, you can add it here.')
    lead_photo = models.ForeignKey(Photo, null=True, blank=True, help_text='Photo will be resized on the template.')
    keywords = models.CharField(max_length=200, blank=True, help_text='Enter a comma-separated list of keywords.')
    description = models.CharField(max_length=200, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE_STATUS, help_text='Only press releases with "Live" status will be displayed.')
    objects = models.Manager()
    live = LiveEntryManager()
        
    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'press release'
        verbose_name_plural = 'press releases'
    
    def __unicode__(self):
        return self.headline

    def save(self):
        self.summary_html = markdown(self.summary)
        super(PressRelease, self).save()
        try:
        	ping_google()
        except Exception:
        	pass
    
    def get_absolute_url(self):
        return '/news/%s/%s/' % (self.pub_date.strftime('%Y/%b/%d').lower(), self.slug)   