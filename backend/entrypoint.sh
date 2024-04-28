#!/bin/sh

python manage.py collectstatic --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input
gunicorn config.wsgi:application --bind 0.0.0.0:8000 
