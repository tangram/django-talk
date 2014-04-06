from django.conf.urls import patterns, include, url

urlpatterns = patterns('talk.views',
    url(r'^$', 'view_thread', name='index'),
    url(r'^threads/$', 'view_thread', name='threads'),
    url(r'^threads/(?P<thread_id>[\d]+)/$', 'view_thread', name='view_thread'),
    url(r'^threads/new/$', 'new_thread', name='new_thread'),
    url(r'^api/$', 'api', name='talk_api'),
    url(r'^api/threads/$', 'thread_search', name='talk_thread_search'),
    url(r'^api/settings/$', 'settings', name='talk_settings'),
)

urlpatterns += patterns('',
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)
