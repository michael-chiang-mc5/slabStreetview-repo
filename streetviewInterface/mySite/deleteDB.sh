#!/bin/bash

rm db.sqlite3
rm -rf ImagePicker/migrations
rm media/*.jpg
python manage.py makemigrations ImagePicker
python manage.py migrate
