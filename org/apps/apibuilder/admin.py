from django.contrib import admin
from models import *
class QLAdmin(admin.ModelAdmin):
    list_display = ('ip', 'user', 'method', 'path', 'query', 'status_code', 'time')
    list_filter = ('ip', 'method', 'status_code', 'time')
    search_fields = ('query','comment')

admin.site.register(QueryLog, QLAdmin)

class MTAdmin(admin.ModelAdmin):
    list_display = ('name','mimetype')

admin.site.register(MimeType, MTAdmin)
admin.site.register(Profile)
admin.site.register(Limit)
admin.site.register(Key)


