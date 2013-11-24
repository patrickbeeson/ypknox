from django.contrib import admin
from ypknox.apps.news.models import PressRelease

class PressReleaseAdmin(admin.ModelAdmin):
	raw_id_fields = ['related_event']
	prepopulated_fields = {'slug': ('headline',)}
	list_display = ('headline', 'slug', 'pub_date')
	list_filter = ('status', 'pub_date', 'category')
	search_fields = ('headline', 'meta_description', 'summary', 'keywords')
	fieldsets = [
		(None, {'fields': ('author', 'pub_date', 'slug', 'headline', 'summary', 'body', 'lead_photo', 'category', 'related_event', 'status'),}),
		('Meta options for SEO', {'fields': ('keywords', 'description'), 'classes': ('collapse',)}),
	]
	raw_id_fields = ('lead_photo',)

admin.site.register(PressRelease, PressReleaseAdmin)