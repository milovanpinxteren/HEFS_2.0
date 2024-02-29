web: gunicorn djangoProject.wsgi
worker: python manage.py rqworker high default low --with-scheduler
release: django-admin migrate --no-input
