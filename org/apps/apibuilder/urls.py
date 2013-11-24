from django.conf.urls.defaults import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

urlpatterns = patterns('django.views.generic.simple',
    (r'^client/$','direct_to_template',{'template':'api/client.html'}),
)

urlpatterns += patterns('apibuilder.views',
    # Example of direct queryset resource (Public)
    # (r'^contenttype/$', 'query', {'queryset':ContentType.objects.all()}),

    # User admin resource (Authentication/Authorization)
    # (r'^users/$', 'auth_query', {'queryset':User.objects.all()}),

    (r'^admin/(?P<app_label>.*)/(?P<model>.*)/(?P<pk>.*)/$', 'auth_query'), # Authenticate
    (r'^admin/(?P<app_label>.*)/(?P<model>.*)/$', 'auth_query'), # Authenticate

    (r'^(?P<app_label>.*)/(?P<model>.*)/(?P<pk>.*)/$', 'query'), # Anonymous
    (r'^(?P<app_label>.*)/(?P<model>.*)/$', 'query'), # Anonymous
)

