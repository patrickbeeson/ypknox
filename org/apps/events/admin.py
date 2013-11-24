from django.contrib import admin
from ypknox.apps.events.models import Event, FeaturedEvent, Location, Attendee
from ypknox.apps.category.models import Category
	

class AttendeeInline(admin.TabularInline):
    model = Attendee
    extra = 3
    fields = ('user', 'attending_status', 'number_of_guests', 'comment')

class EventAdmin(admin.ModelAdmin):
	list_display = ('name', 'event_date', 'category', 'location', 'attire', 'rsvp', 'audience', 'payments_accepted')
	list_filter = ('event_date', 'category', 'audience', 'attire', 'payments_accepted', 'rsvp')
	search_fields = ('name', 'description')
	prepopulated_fields = {'slug': ('name',)}
	fieldsets = [
		(None, {'fields': ('slug', 'name', 'location', 'event_leader', 'audience', 'description', 'event_date', 'start_time', 'finish_time', 'lead_photo', 'rsvp', 'payments_accepted', 'attire', 'category',),}),
		('Meta options for SEO', {'fields': ('keywords',), 'classes': ('collapse',)}),
	]
	inlines = [AttendeeInline]
	raw_id_fields = ('lead_photo',)

admin.site.register(Event, EventAdmin)

class AttendeeAdmin(admin.ModelAdmin):
    fields = ('event', 'user', 'attending_status', 'number_of_guests', 'comment')
    list_display = ('user', 'event', 'attending_status', 'number_of_guests')
    list_filter = ('attending_status',)
    search_fields = ('user', 'event')

admin.site.register(Attendee, AttendeeAdmin)

class FeaturedEventAdmin(admin.ModelAdmin):
	list_display = ('name', 'live_date', 'event_to_feature', 'featured_event_photo',)
	raw_id_fields = ('event_to_feature', 'featured_event_photo',)

admin.site.register(FeaturedEvent, FeaturedEventAdmin)

class LocationAdmin(admin.ModelAdmin):
	list_display = ('name', 'prename')
	search_fields = ('name', 'description')
	prepopulated_fields = {'slug': ('name', 'prename',)}

admin.site.register(Location, LocationAdmin)