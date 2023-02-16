from django.core.management import BaseCommand
from django.db import transaction

from ecoloweb.services.query_iterator import QueryResultIterator
from programmes.models import IndiceEvolutionLoyer


class Command(BaseCommand):
    help = "Import loyers indices form Ecoloweb database"

    def handle(self, *args, **options):
        """
        Règles de calcul:

        Il existe 3 indices annuels : ICC, IRL1 et IRL2, (les indices trimestriels ne sont plus utilisés)
            * l'ICC est valable avant 2005 (2005 inclus)
            * l'IRL1 est valable pour 2006 et 2007
            * l'IRL2 est valable depuis 2008.

        À partir de l'année de dernière révision N, le loyer révisé de l'année N+1= loyer année N * ((100 + indice de l'année N+1)/100)
        """
        results: QueryResultIterator = QueryResultIterator(
            query="""
select vps.libelle::int as annee, coalesce(il.irl2evol, il.irl1evol, il.iccaugmentation, il.icctrim4moyenne) as coefficient
from ecolo.ecolo_indiceloyer il
    inner join ecolo.ecolo_valeurparamstatic vps on il.annee_id = vps.id
        """
        )

        with transaction.atomic():
            for result in results:
                IndiceEvolutionLoyer.objects.update_or_create(
                    defaults=result, annee=result["annee"]
                )
