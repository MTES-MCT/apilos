from django.core.management.base import BaseCommand
from django.db.models import Count

from programmes.models import Programme


class Command(BaseCommand):
    def handle(self, *args, **options):
        Programme.objects.all().annotate(convention_count=Count("conventions")).filter(
            convention_count=0
        ).delete()
