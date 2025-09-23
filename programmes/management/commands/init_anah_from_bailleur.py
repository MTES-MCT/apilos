from django.core.management.base import BaseCommand

from bailleurs.models import Bailleur
from programmes.models.models import Programme


class Command(BaseCommand):
    help = (
        "Met à jour le champ anah à True pour tous les programmes associés aux "
        'bailleurs dont le nom commence par "ANAH"'
    )

    def handle(self, *args, **options):
        # On recupère tous les bailleurs dont le nom commence par "ANAH"
        bailleurs_anah = Bailleur.objects.filter(nom__startswith="ANAH")
        Programme.objects.filter(bailleur__in=bailleurs_anah).update(anah=True)


        self.stdout.write(
            self.style.SUCCESS(
                "Successfully updated all programmes from ANAH bailleurs."
            )
        )
