from django_extensions.management.jobs import BaseJob
import traceback

from eve.lib import eveapi
from eve.settings import DEBUG
from eve.user.models import UserProfile

#from Queue import Queue
#import workerpool

class Job(BaseJob):
    help = "Reload all of the alliances and member corporations."
    when = '5min'

    def execute(self):
        update_users()

def update_users(user=None, force=False):
    messages = []
    api = eveapi.get_api()

    if user:
        print("Only loading characters for: %s" % user)
        users = UserProfile.objects.filter(user__username=user)
    else:
        # All the non-stale users.
        users = [u for u in UserProfile.objects.all() if not u.is_stale]

    if force:
        print("Forcing reload, cache times will be ignored.")

    for u in users:
        print  "-" * 77
        print "User: %s" % u
        error = False
        m = []
        for a in u.accounts.all():
            print "  " + ('- ' * 38)
            print "  Account: %s" % a.id
            try:
                messages = a.refresh(force=force)
            except Exception, e:
                m.append(traceback.format_exc())
                if DEBUG:
                    raise
            for x in messages:
                print "  -- %s" % x['name']
                for m in x['messages']:
                    print "    " + m
            if error:
                print "    Fatal error occured."
                print "    " + error
