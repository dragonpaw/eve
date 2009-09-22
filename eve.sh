#!/bin/sh

PROJECT='/home/ash/django-sites/eve'
PIDFILE="$PROJECT/log/django.pid"
PORT=3033
MAX=5000

cd $PROJECT
if [ -f $PIDFILE ]; then
    PID=`cat -- $PIDFILE`
    echo "Killing: $PID"
    kill $PID
    rm -f -- $PIDFILE
fi

echo "Starting..."
/usr/bin/env - \
    PYTHONPATH="../python:.." \
    ./manage.py runfcgi host=127.0.0.1 port=$PORT pidfile=$PIDFILE daemonize=true method=threaded maxchildren=1 manspare=1 maxrequests=$MAX

echo "Loading home page to initialize app..."
wget http://eve.magicwidget.net/ -O /dev/null
