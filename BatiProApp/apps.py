from django.apps import AppConfig


class BatiproappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BatiProApp'
    def ready(self):
        import BatiProApp.signals  
