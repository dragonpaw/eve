from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from eve.tracker.models import ChangeLog

def changelog(request):
    d = {}
    
    d['nav'] = [{'name':'Changelog','get_absolute_url':'/changelog'}]
    d['title'] = "Change Log"
    
    d['logs'] = ChangeLog.objects.all()
    return render_to_response('tracker_changelog.html', d)
