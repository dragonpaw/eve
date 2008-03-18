from eve.tracker.models import ChangeLog
from django.http import HttpResponseRedirect
from datetime import datetime

class ChangeLogMiddleware:
    def process_request(self, request):
        if request.user.is_anonymous():
            return None
        if ChangeLog.objects.count() == 0:
            return None
    
        newest_changelog = ChangeLog.objects.order_by('-date')[0].date
    
        if request.user.last_login < newest_changelog:
            request.user.last_login = datetime.now()
            request.user.save()
            return HttpResponseRedirect('/changelog/%s/' % request.user.last_login.strftime('%Y-%m-%d-%H:%M'))
        else:
            return None