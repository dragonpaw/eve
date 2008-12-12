from eve.tracker.models import Ticket, ChangeLog
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class TicketOptions(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'submitter', 
        'submitted_date', 'modified_date')
    list_filter = ('priority', 'status', 'submitted_date')
    search_fields = ('title', 'description',)

class ChangeLogOptions(admin.ModelAdmin):
    list_display = ('date', 'description')
    search_fields = ('date', 'description')

admin.site.register(Ticket, TicketOptions)
admin.site.register(ChangeLog, ChangeLogOptions)

