web: gunicorn djangoProject.wsgi
worker: python manage.py rqworker high default low
celery_worker: celery -A djangoProject worker --loglevel=info
release: django-admin migrate --no-input
