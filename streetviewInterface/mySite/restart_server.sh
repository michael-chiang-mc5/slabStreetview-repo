#!/bin/bash

python manage.py collectstatic
pkill -f /home/michaelc/dev/slabStreetview-repo/streetviewInterface/venv/bin/gunicorn 
# python manage.py migrate --run-syncdb
gunicorn mySite.wsgi --bind 127.0.0.1:8004 --daemon --log-file ~/dev/logs/slab.log --workers=1
