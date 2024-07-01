from django.apps import AppConfig


class EmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emissions'

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        import emissions.templatetags.custom_filters
