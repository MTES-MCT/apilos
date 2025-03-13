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
            "libo": "Libourne",
            "les molettes": "Les Mollettes",
            "NEUF": "Neufchâtel-Hardelot",
            "SAINT-CHRISOPHE DE DOUBLE": "Saint-Christophe-de-Double",
            "SAN MARINA DI LOTA": "Santa-Maria-di-Lota",
            "LAMBRES LES DOUAI": "LAMBRES LEZ DOUAI",
            "CHAU": "Chaumont",
            "NANTEUIL LE HAUDOIN": "NANTEUIL LE HAUDOUIN",
            "ST LEU DESSERENT": "Saint-Leu-d'Esserent",
            "SAINT PANTALEON DE L ARCHE": "SAINT PANTALEON DE LARCHE",
            "STIRING WENEL": "STIRING WENDEL",
            "SAINT-JUSTE-IBARRE": "Saint-Just-Ibarre",
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
            "billy-berclau": "62138",
            "vaux-sur-seine": "78740",
            "mignovillard": "39250",
            "Aubigny-Les Clouzeaux": "85430",
            "Enghien-les-Bains": "95880",
            "pontoise les noyon": "60400",
            "Puget-sur-Argens": "83480",
            "Pontault-Combault": "77340",
            "Ferney-Voltaire": "01210",
            "coursan": "11110",
            "ARNAC POMPADOUR": "19230",
            "Morangis": "91420",
            "FERRALS-LES-CORBIERES": "11200",
            "Les Sorinières": "44840",
            "La Gorgue": "59253",
            "BARBY": "73230",
            "Houlbec-Cocherel": "27120",
        }.items():
            queryset = Programme.objects.filter(ville__iexact=k).exclude(code_postal=v)
            if count := queryset.count():
                self.stdout.write(f"{count} codes postaux mis à jour pour '{k}'")
                queryset.update(code_postal=v)

        # problème avec le "œ"
        Programme.objects.filter(ville="Annœullin").update(code_insee_commune="59112")
        Programme.objects.filter(ville="Crèvecœur le grand").update(
            code_insee_commune="60178"
        )

        # Cournon existe aussi, mais dans le morbihan
        Programme.objects.filter(pk__in=(644694, 644695)).update(
            ville="Cournon-d'Auvergne"
        )

        # Divers, unitaires
        Programme.objects.filter(pk=34847).update(code_postal="76600")
        Programme.objects.filter(pk=647779).update(code_postal="02120")
        Programme.objects.filter(pk=651951).update(
            code_postal="18190", code_insee_commune="18270"
        )
