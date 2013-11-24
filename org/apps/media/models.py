from django.db import models
import datetime
from markdown import markdown

class Photo(models.Model):
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	title = models.CharField(max_length=50)
	slug = models.SlugField(unique_for_date='pub_date', help_text='Slug prepopulates from title')
	photo = models.ImageField(upload_to='images/photos', width_field='photo_width', height_field='photo_height')
	caption = models.TextField(help_text='A brief summary of this category. Use <a href="http://daringfireball.net/projects/markdown/syntax">Markdown syntax</a>.')
	caption_html = models.TextField(editable=False, blank=True)
	credit = models.CharField(max_length=100, help_text='If you wish to give credit to a photographer, add their name here.', blank=True)
	photo_width = models.IntegerField(default=0, null=True, help_text='The photo width in pixels. This field will populate when the photo is saved.')
	photo_height = models.IntegerField(default=0, null=True, help_text='The photo height in pixels. This field will populate when the photo is saved.')
	external_url = models.URLField(help_text='If the photo is located on an external Web site, please add the URL here.', blank=True)

	class Meta:
		verbose_name_plural = 'photos'

	def __unicode__(self):
		return self.title

	def save(self):
		self.caption_html = markdown(self.caption)
		super(Photo, self).save()