from django.contrib import admin
from ypknox.apps.user_profiles.models import Profile
from django.contrib import databrowse

class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'employer',)
	list_filter = ['is_public']

admin.site.register(Profile, ProfileAdmin)
databrowse.site.register(Profile)