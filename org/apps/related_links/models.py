from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class RelatedLink(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(db_index=True)
    content_object = generic.GenericForeignKey()
    url = models.URLField('URL')
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title