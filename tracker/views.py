from datetime import datetime
import time

from lib.jinja import render_to_response
from lib.formatting import NavigationElement
from tracker.models import ChangeLog

changelog_nav = NavigationElement(
    "Changes", "/changelog/", '10_16', 'Updates to the Widget.'
)

def changelog(request, when=None):
    d = {}

    d['nav'] = [changelog_nav]
    if when:
        when = datetime(*time.strptime(when, "%Y-%m-%d-%H:%M")[0:5])
        d['logs'] = ChangeLog.objects.filter(date__gte=when)
        d['nav'].append({'name':'Since you last logged in'})
    else:
        d['logs'] = ChangeLog.objects.all()

    if request.user.is_anonymous() is False:
        profile = request.user.get_profile()
        profile.last_read_changelog = datetime.utcnow()
        profile.save()

    return render_to_response('tracker_changelog.html', d, request)
