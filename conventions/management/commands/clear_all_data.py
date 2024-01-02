import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from bailleurs.models import Bailleur
from ecoloweb.models import EcoloReference
from instructeurs.models import Administration
from users.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.ENVIRONMENT in ["production", "siap-production"]:
            logger.error("This action can't be called in production environment")
            return
        with transaction.atomic():
            Administration.objects.all().delete()
            logger.info("Administration were cleared")
            Bailleur.objects.all().delete()
            logger.info("Bailleur were cleared")
            User.objects.exclude(is_superuser=True).exclude(is_staff=True).delete()
            logger.info("non staff and superuser User were cleared")
            EcoloReference.objects.all().delete()
