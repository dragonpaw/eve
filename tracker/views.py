from django.shortcuts import render_to_response
from eve.tracker.models import ChangeLog
from eve.util.formatting import make_nav

changelog_nav = make_nav("Changes", "/changelog/", '10_16', note='Updates to the Widget.')

def changelog(request):
    d = {}
    
    d['nav'] = [changelog_nav]
    
    d['logs'] = ChangeLog.objects.all()
    return render_to_response('tracker_changelog.html', d)
