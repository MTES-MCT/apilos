from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Vérifie et corrige les codes INSEE departementaux"

    def handle(self, *args, **options):
        pass
        # TODO: implement this command
