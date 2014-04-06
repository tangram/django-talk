from django.contrib import admin
from models import Message, Thread, MessageIndex, Settings


class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', '__unicode__', 'created_at']
    search_fields = ['author']


class ThreadAdmin(admin.ModelAdmin):
    list_display = ['user_list', 'updated_at']
    search_fields = ['users']


class MessageIndexAdmin(admin.ModelAdmin):
    list_display = ['message', 'thread', 'user', 'new']
    search_fields = ['message', 'user']


class SettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications']
    search_fields = ['user']


admin.site.register(Message, MessageAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(MessageIndex, MessageIndexAdmin)
admin.site.register(Settings, SettingsAdmin)
