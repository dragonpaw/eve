from django_extensions.management.jobs import BaseJob
import traceback

from eve.lib import eveapi
from eve.settings import DEBUG
from eve.user.models import Account

#from Queue import Queue
#import workerpool

class Job(BaseJob):
    help = "Reload all of the alliances and member corporations."

    def execute(self):
        update_users()

def update_users(user=None, force=False):
    messages = []
    api = eveapi.get_api()

    if user:
        print("Only loading characters for: %s" % user)
        accounts = Account.objects.filter(user__user__username=user)
    else:
        accounts = Account.objects.all()

    if force:
        print("Forcing reload, cache times will be ignored.")

    for account in accounts:
        error = False
        m = []
        try:
            messages = account.refresh(force=force)
        except Exception, e:
            m.append(traceback.format_exc())
            if DEBUG:
                raise
        print  "-" * 78
        print "Account: %s(%s)" % (account.user, account.id)
        for x in messages:
            print "-- %s" % x['name']
            print "  " +("\n  ".join(x['messages']))
        if error:
            print "Fatal error occured."
            print error
