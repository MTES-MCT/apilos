from django.core.management.base import BaseCommand

from programmes.models import Programme


class Command(BaseCommand):
    help = "Fix communes names"

    def handle(self, *args, **options):
        for k, v in {
            "croisille": "Croisilles",
            "capavenir vosges": "Thaon-les-Vosges",
            "le luc en provence": "Le Luc",
            "guesnain coron sans beurre": "Guesnain",
            "hoodschoote": "Hondschoote",
            "chamamont": "Chalamont",
            "le viviers du lac": "Viviers-du-Lac",
            "mesnil en thelle": "Le Mesnil-en-Thelle",
            "saint remy les chevreuses": "Saint-Rémy-lès-Chevreuse",
            "isle sur la sorgue": "L'Isle-sur-la-Sorgue",
            "conde sur escaut": "Condé-sur-l'Escaut",
        }.items():
            queryset = Programme.objects.filter(ville__iexact=k)
            if count := queryset.count():
                self.stdout.write(f"{count} noms de ville mis à jour pour '{v}'")
                queryset.update(ville=v)

        for k, v in {
            "biot": "06410",
            "maing": "59233",
            "vaux sur seine": "78740",
            "gournay sur aronde": "60190",
            "seclin": "59113",
            "wittelsheim": "68310",
            "billy berclau": "62138",
            "vaux-sur-seine": "78740",
            "mignovillard": "39250",
        }.items():
            queryset = Programme.objects.filter(ville__iexact=k).exclude(code_postal=v)
            if count := queryset.count():
                self.stdout.write(f"{count} codes postaux mis à jour pour '{k}'")
                queryset.update(code_postal=v)
