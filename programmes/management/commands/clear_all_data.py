import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from instructeurs.models import Administration
from bailleurs.models import Bailleur
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.ENVIRONMENT in ["production", "siap-production"]:
            logging.error("This action can't be called in production environment")
            return
        print("Let's remove all")
        Administration.objects.all().delete()
        Bailleur.objects.all().delete()
        User.objects.exclude(is_superuser=True).exclude(is_staff=True).delete()
