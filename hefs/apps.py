import sys

from django.apps import AppConfig




class HighendfoodsolutionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hefs'

    def ready(self):
        print('APPS.PY ready function')
        print(sys.argv)
        if 'runserver' in sys.argv:
            print('runserver not')

            from djangoProject.scheduler import schedule_task
            schedule_task()

