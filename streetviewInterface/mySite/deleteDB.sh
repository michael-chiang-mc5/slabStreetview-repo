#!/bin/bash

rm db.sqlite3
rm -rf ImagePicker/migrations
rm media/*.jpg
python manage.py makemigrations ImagePicker
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | ./manage.py shell

