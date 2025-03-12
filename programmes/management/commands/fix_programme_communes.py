from django.core.management.base import BaseCommand

from programmes.models import Programme


class Command(BaseCommand):
    help = "Fix communes names"

    def handle(self, *args, **options):
        for k, v in {
            "croisille": "Croisilles",
            "lamballe ARMOR": "Lamballe",
            "capavenir vosges": "Thaon-les-Vosges",
            "le luc en provence": "Le Luc",
        }.items():
            queryset = Programme.objects.filter(ville__iexact=k)
            if count := queryset.count():
                self.stdout.write(f"{count} noms de villes mis à jour pour '{k}'")
                queryset.update(ville=v)

        for k, v in {"biot": "06410"}.items():
            queryset = Programme.objects.filter(ville__iexact=k).exclude(code_postal=v)
            if count := queryset.count():
                self.stdout.write(f"{count} codes postaux mis à jour pour '{k}'")
                queryset.update(code_postal=v)
