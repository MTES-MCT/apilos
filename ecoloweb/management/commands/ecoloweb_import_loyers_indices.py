from django.core.management import BaseCommand
from django.db import transaction

from ecoloweb.services.query_iterator import QueryResultIterator
from programmes.models import IndiceEvolutionLoyer


class Command(BaseCommand):
    help = "Import loyers indices form Ecoloweb database"

    def handle(self, *args, **options):
        """
        Règles de calcul :

        Il existe 3 indices annuels : ICC, IRL1 et IRL2, (les indices trimestriels ne sont plus utilisés)
            * l'ICC est valable avant 2005 (2005 inclus)
            * l'IRL1 est valable pour 2006 et 2007
            * l'IRL2 est valable depuis 2008.

        À partir de l'année de dernière révision N, le loyer révisé de l'année N+1= loyer année N * ((100 + indice de l'année N+1)/100)
        """
        results: QueryResultIterator = QueryResultIterator(
            query="""
select vps.libelle::int as annee, 'LOGEMENTSORDINAIRES' as nature_logement, coalesce(il.irl2evol, il.irl1evol, il.iccaugmentation, il.icctrim4moyenne / 100.) as differentiel
from ecolo.ecolo_indiceloyer il
    inner join ecolo.ecolo_valeurparamstatic vps on il.annee_id = vps.id
        """
        )

        with transaction.atomic():
            for result in results:
                IndiceEvolutionLoyer.objects.update_or_create(
                    defaults=result,
                    annee=result["annee"],
                    nature_logement=result["nature_logement"],
                )

        results: QueryResultIterator = QueryResultIterator(
            query="""
select distinct on (ir.annee, ir.nature_logement) ir.annee, ir.nature_logement, ir.differentiel
from (
    select
        vps.libelle::int as annee,
        case
            when nl.code = '6' then 'RESISDENCESOCIALE'
        else 'AUTRE' end as nature_logement,
        coalesce(ir.indicevariation, 1.) as differentiel
    from ecolo.ecolo_indiceredevance ir
        inner join ecolo.ecolo_valeurparamstatic vps on ir.annee_id = vps.id
        inner join ecolo_naturelogement nl on ir.naturelogement_id = nl.id
    where nl.code <> '1' --LOGEMENTSORDINAIRES
) ir
                """
        )

        with transaction.atomic():
            for result in results:
                IndiceEvolutionLoyer.objects.update_or_create(
                    defaults=result,
                    annee=result["annee"],
                    nature_logement=result["nature_logement"],
                )
