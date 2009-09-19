#!/usr/bin/python
import sys, os, signal, time

PID_FILE = 'django.pid'
WORK_DIR = '/home/ash/django-sites/eve'
PORT     = 3033
DAEMON   = True
METHOD   = 'fork'
MAX_REQUESTS = 1000
HOST     = '127.0.0.1'
MAX_CHILDREN = 3

# Add a custom Python path.
sys.path.insert(0, "/home/ash/django-sites")

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/myproject")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "eve.settings"

PID_FILE = os.path.join(WORK_DIR, PID_FILE)
if os.path.exists(PID_FILE):
  file = open(PID_FILE)
  pid = int( file.read() )
  try:
    os.kill(pid, signal.SIGTERM)
    time.sleep(5) # Give it time to shutdown
  except: 
    pass
  os.unlink(PID_FILE)

if DAEMON:
  DAEMON = 'true'
else:
  DAEMON = 'false'

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method      = METHOD, 
           daemonize   = DAEMON, 
           workdir     = WORK_DIR, 
           port        = PORT, 
           maxrequests = MAX_REQUESTS,
           maxChildren = MAX_CHILDREN,
           host        = HOST, 
           pidfile     = PID_FILE,
)

