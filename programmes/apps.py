from django.apps import AppConfig


class ProgrammesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "programmes"

    def ready(self) -> None:
        import programmes.signals  # noqa: F401
