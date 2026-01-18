from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Fitness Tracker'

    def ready(self):
        """
        Docstring for ready
        
        Import signal handlers when the app is ready
        This ensures signals are registered
        """
        import fitness.signals #noqa