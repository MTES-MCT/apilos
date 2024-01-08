from django.apps import AppConfig


class ConventionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conventions"

    def ready(self) -> None:
        import conventions.signals  # noqa: F401
