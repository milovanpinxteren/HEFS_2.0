web: gunicorn djangoProject.wsgi
worker: python worker.py
release: sh -c 'django-admin migrate --no-input && python manage.py rqworker high default low &'
