#import os, mailbox, email, datetime, shutil, sys
import datetime, os, sys, email

# Ya might need this.
#os.environ["DJANGO_SETTINGS_MODULE"] = "eve.settings"  

from email.Utils import parsedate  # change to email.utils for Python 2.5

from emails.models import Message
from django.contrib.auth.models import User 

#print sys.stdin

message = email.message_from_file(sys.stdin)

try:
    date = datetime.datetime(*parsedate(message['date'])[:6])
except TypeError:  # silently ignore badly-formed dates
    date = datetime.datetime.now()

try:
    user = User.objects.get(email=message['to'])
    profile = user.get_profile()
except:
    print "Unable to find a user %s" % message['to']

try:        
    msg = Message(
                  profile=profile,
                  subject=message['subject'],
                  date=date,
                  to_address=message['to'],
                  from_address=message['from'],
                  body=message.get_payload(decode=False),
        )
    print "Adding: %s..." % msg.subject[:40]
    msg.save()
except:
    print "Trouble parsing message (%s...)" % message['subject'][:40]