from django.apps import AppConfig


class BatchesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.batches"        # путь к модулю
    verbose_name = "Партии"
    