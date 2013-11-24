from django.db import models
from markdown import markdown

class Category(models.Model):
    slug = models.SlugField(help_text='This field will prepopulate from the title field.', unique=True)
    title = models.CharField(max_length=50)
    description = models.TextField(help_text='A brief summary of this category. Use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown syntax</a>.')
    description_html = models.TextField(editable=False, blank=True)
    keywords = models.CharField(max_length=200, help_text='Comma-separated keywords describing the category. Limit 200 characters.', blank=True)
        
    class Meta:
        verbose_name_plural = 'categories'
        
    def __unicode__(self):
        return self.title

    def save(self):
        self.description_html = markdown(self.description)
        super(Category, self).save()
    
    def get_absolute_url(self):
        return '/categories/%s/' % (self.slug)

    def live_pressrelease_set(self):
    	""" Returns live pressreleases for a category """
        from ypknox.apps.news.models import PressRelease
        return self.pressrelease_set.filter(status=PressRelease.LIVE_STATUS)

    def current_event_set(self):
    	""" Returns current events for a category """
        from ypknox.apps.events.models import Event
        import datetime
        return self.event_set.filter(event_date__gte=datetime.date.today())