#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'
os.environ['TZ'] = 'UTC'

from eve.lib.cachehandler import MyCacheHandler
from datetime import datetime, timedelta
from exceptions import Exception
from eve.lib import eveapi
import time
import sys
import traceback

from eve.user.models import Account
from eve.settings import DEBUG

character_security_timeout = timedelta(hours=12)

def get_api(debug=DEBUG):
    api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=debug, throw=False)).context(version=2)
    return api

# Depricated
def exit():
    output("Runtime: %s" % (datetime.utcnow() - start_time))
    if exit_code != 0 and not options.verbose:
        print message
    sys.exit(exit_code)


def update_users(user=None, force=False):
    messages = ['Starting user refresh...']
    api = get_api()

    if user:
        messages.append("Only loading characters for: %s" % user)
        accounts = Account.objects.filter(user__user__username=user)
    else:
        accounts = Account.objects.all()

    if force:
        messages.append("Forcing reload, cache times will be ignored.")

    for account in accounts:
        messages.append("Account: %s(%s)" % (account.user, account.id))
        error = False
        m = []
        try:
            messages.extend( account.refresh(force=force) )
        except Exception, e:
            m.append(traceback.format_exc())
            if DEBUG:
                raise

if __name__ == '__main__':
    exit_code = 0
    message = ''
    start_time = datetime.utcnow()

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-u', '--user',
                      help='Username to load accounts for.')
    parser.add_option('-f', '--force', action='store_true', default=False,
                      help='Force reload of cached data.')
    parser.add_option('-d', '--debug', action='store_true', default=DEBUG,
                      help='Be really chatty.')

    (options, args) = parser.parse_args()

    if options.debug:
        DEBUG = True

    update_users(user=options.user, force=option.force)
