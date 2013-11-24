from ypknox.apps.media.models import Photo
from django.contrib import admin

class PhotoAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug')
	search_fields = ('title', 'caption')
	prepopulated_fields = {'slug': ('title',)}

admin.site.register(Photo, PhotoAdmin)