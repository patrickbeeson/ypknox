from django.contrib import admin
from ypknox.apps.links.models import Link

class LinkAdmin(admin.ModelAdmin):
	list_display = ('URL', 'link_title')
	list_filter = ['category']

admin.site.register(Link, LinkAdmin)