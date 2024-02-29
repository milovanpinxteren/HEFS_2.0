from django.apps import AppConfig

from djangoProject.scheduler import schedule_task


class HighendfoodsolutionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hefs'

    def ready(self):
        schedule_task()

