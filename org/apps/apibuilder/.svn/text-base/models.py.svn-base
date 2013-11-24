from urllib import urlencode,quote

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User,get_hexdigest

import apibuilder

class QLManager(models.Manager):
    def create_from_transaction(self, request, response, msg):
        try:
            msg = unicode(msg[:100])
        except UnicodeDecodeError:
            msg = quote(msg[:100])[:100]
        user = None
        if hasattr(request, 'user'):
            user = request.user
        return self.create(
            ip = apibuilder.get_ip(request),
            path = request.path[:255],
            user = user,
            query = urlencode(request.GET.items()),
            status_code = response.status_code,
            comment = msg,
            method = request.method
        )

class QueryLog(models.Model):
    method = models.CharField(max_length=6)
    ip = models.IPAddressField(blank=True,null=True)
    user = models.ForeignKey(User,blank=True,null=True)
    query = models.TextField(blank=True,null=True)
    path = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField()
    comment = models.CharField(max_length=100)
    
    objects = QLManager()
    
    def __unicode__(self):
        return u'%s: %s' % (self.user, self.query)

class MimeType(models.Model):
    name = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name

class PManager(models.Manager):
    def get_current(self):
        if hasattr(self,'_cachedprofile'):
            return self._cachedprofile
        try:
            self._cachedprofile = self.filter(enabled=True)[0]
        except IndexError:
            self._cachedprofile = self.create(enabled=True)
        return self._cachedprofile
    
class Profile(models.Model):
    name = models.CharField(max_length=100,unique=True)
    default_format = models.ForeignKey(MimeType, default=2)
    realm = models.CharField(max_length=255,
            help_text='Realm to use for auth',default='Authenticated Query API')
    default_timeout = models.FloatField(default=60*15,
            help_text='Default cache timeout')
    jsonp = models.CharField(max_length=255, default='jsoncallback',
            help_text='JSONP variable name (allows scripting from other domains)')
    enabled = models.BooleanField(default=True)
    
    allowed_ips = models.TextField(blank=True,default='()',
                        help_text='Tuple of allowed IP addresses or hostnames')
    allowed_users = models.TextField(blank=True,default='()',
                        help_text='Tuple of allowed usernames')
    denied_ips = models.TextField(blank=True,default='()',
                        help_text='Tuple of denied IP addresses or hostnames')
    denied_users = models.TextField(blank=True,default='()',
                        help_text='Tuple of denied usernames')
    order = models.TextField(blank=True,default='()')

    objects = PManager()

    def eval(self, field):
        return eval(getattr(self,field),{},{})

    def __unicode__(self):
        return self.name

class Limit(models.Model):
    criteria = models.CharField(max_length=255,unique=True,
        help_text='Must be one of anonymous/authenticated/staff/superuser or any username')
    queryset_length = models.IntegerField(default=100)
    content_length = models.IntegerField(default=-1)
    
    timeout = models.TextField(default='900', help_text='Cache timeout')
    model_map = models.TextField(blank=True)

    def eval_timeout(self):
        try:
            return eval(self.timeout,{},{})
        except:
            return
    
    def __unicode__(self):
        return self.criteria

class Key(models.Model):
    key = models.CharField(max_length=255,blank=True)
    user = models.ForeignKey(User)
    hostname = models.CharField(max_length=200)
    
    def save(self, *a, **kw):
        if not self.key:
            self.key = get_hexdigest('sha1', self.hostname,  self.user.username)
        super(Key, self).save(*a, **kw)
        
    class Meta:
        unique_together = ('key','user','hostname')
        
    def __unicode__(self):
        return self.key

# Ellington Extras
if 'ellington.news' in settings.INSTALLED_APPS:

    from ellington.news.parts.markup import sml_to_xhtml
    from apibuilder import transform
    
    def story_transformer(story):
        story.story = sml_to_xhtml(story)
        return story
    
    transform.register('news.story',story_transformer)


