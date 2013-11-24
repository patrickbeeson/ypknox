from django.db import models
from ypknox.apps.category.models import Category

class Link(models.Model):
	URL = models.URLField()
	linked_text = models.CharField(max_length=200)
	link_title = models.CharField(max_length=200)
	new_window = models.BooleanField(default=False, help_text='Check this box to have the link open in a new window. Default is false.')
	category = models.ForeignKey(Category)
	
	class Meta:
		verbose_name_plural = 'links'
        
	def __unicode__(self):
		return self.link_title