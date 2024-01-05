from django.core.management.base import BaseCommand
from django.db.models import F
from waffle.models import Flag

from bailleurs.models import Bailleur
from programmes.models import Programme


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(
            ">> Création du flag 'nouvelle_recherche' pour activer la nouvelle recherche des conventions"
        )
        Flag.objects.get_or_create(
            name="nouvelle_recherche",
            defaults={
                "note": "Active la nouvelle recherche des conventions",
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Ok! Rendez vous dans /admin/waffle/flag/ pour éditer ce flag"
            )
        )

        self.stdout.write(
            ">> Mise à jour de tous les programmes pour peupler le nouveau champs search_vector"
        )
        Programme.objects.update(nom=F("nom"))

        self.stdout.write(
            ">> Mise à jour de tous les bailleurs pour peupler le nouveau champs search_vector"
        )
        Bailleur.objects.update(nom=F("nom"))

        self.stdout.write(
            self.style.SUCCESS(
                "Ok! Vous pouvez maintenant vous enregistrer dans l'admin pour utiliser la nouvelle recherche"
            )
        )
