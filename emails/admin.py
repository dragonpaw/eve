from eve.emails.models import Message
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class MessageOptions(admin.ModelAdmin):
    search_fields = ('subject',)
    list_display = ('profile', 'subject',) 

admin.site.register(Message, MessageOptions)

