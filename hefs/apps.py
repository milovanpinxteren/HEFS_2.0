import sys

from django.apps import AppConfig


class HighendfoodsolutionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hefs'

    def ready(self):
        print('APPS.PY ready function')
        print(sys.argv)
        if 'djangoProject.wsgi' in sys.argv:
            print('server served')
            from djangoProject.scheduler import start_schedule_tasks
            start_schedule_tasks()

