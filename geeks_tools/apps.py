from django.apps import AppConfig


class GeeksToolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'geeks_tools'

    def ready(self):
        import geeks_tools.signals 


