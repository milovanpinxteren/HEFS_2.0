web: gunicorn djangoProject.wsgi
worker: python manage.py rqworker high default low
release: django-admin migrate --no-input
