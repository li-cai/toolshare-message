from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^sendmessage', 'message.views.sendmessage'),
    url(r'^inbox', 'message.views.inbox'),
    url(r'^reply/(?P<message_id>\d+)', 'message.views.reply'),
    url(r'^delete/(?P<message_id>\d+)', 'message.views.delete'),
    url(r'^history', 'message.views.history'),
)