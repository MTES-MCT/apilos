from django.core.management import BaseCommand
from django.db import transaction

from ecoloweb.services.query_iterator import QueryResultIterator
from programmes.models import IndiceEvolutionLoyer


class Command(BaseCommand):
    help = "Import loyers indices form Ecoloweb database"

    def handle(self, *args, **options):
        """
        Règles de calcul :

        Il existe 3 indices annuels ICC, IRL1 et IRL2 (les indices
        trimestriels ne sont plus utilisés):
            * l'ICC est valable avant 2005 (2005 inclus)
            * l'IRL1 est valable pour 2006 et 2007
            * l'IRL2 est valable depuis 2008.

        À partir de l'année de dernière révision N, le loyer révisé de l'année
        N+1= loyer année N * ((100 + indice de l'année N+1)/100)
        """
        results: QueryResultIterator = QueryResultIterator(
            query="""
-- Si >= 2009 alors IRL2 T2 et janv -> déc
-- Si entre 2006 et 2008 alors IRL2 T4 et juil -> juin
-- Si entre 2004 et 2006 alors IRL1 T4 et juil -> juin
-- Si entre 1993 et 2004 alors moyenne ICC T4 et juil -> juin
-- Si < 1993 ICC T4 et juil -> juin
select
    vps.libelle::int as annee,
    case
        when vps.libelle::int > 2010 then make_date(vps.libelle::int - 1, 1, 1)
        else make_date(vps.libelle::int - 1, 7, 1)
    end as date_debut,
    case
        when vps.libelle::int >= 2010 then make_date(vps.libelle::int - 1, 12, 31)
        else make_date(vps.libelle::int, 6, 30)
    end as date_fin,
    true as is_loyer,
    null as nature_logement,
    case
        when vps.libelle::int >= 2008 then il.irl2evol
        when vps.libelle::int between 2006 and 2007 then il.irl1evol
        else il.iccaugmentation
    end as evolution
from ecolo.ecolo_indiceloyer il
    inner join ecolo.ecolo_valeurparamstatic vps on il.annee_id = vps.id
where coalesce(il.irl2evol, il.irl1evol, il.iccaugmentation) is not null
        """
        )

        with transaction.atomic():
            for result in results:
                IndiceEvolutionLoyer.objects.update_or_create(
                    defaults=result,
                    date_debut=result["date_debut"],
                    date_fin=result["date_fin"],
                    nature_logement=result["nature_logement"],
                )

        results: QueryResultIterator = QueryResultIterator(
            query="""
select
    distinct on (ir.annee, ir.nature_logement)
    ir.annee,
    case
        when ir.annee > 2010 then make_date(ir.annee - 1, 1, 1)
        else make_date(ir.annee - 1, 7, 1)
    end as date_debut,
    case
        when ir.annee >= 2010 then make_date(ir.annee - 1, 12, 31)
        else make_date(ir.annee, 6, 30)
    end as date_fin,
    false as is_loyer,
    ir.nature_logement,
    ir.evolution
from (
    select
        vps.libelle::int as annee,
        case
            when nl.code = '1' then 'LOGEMENTSORDINAIRES' -- Logements ordinaires
            when nl.code in ('4', '6') then 'RESISDENCESOCIALE' -- Résidences sociales, Logements foyers pour travailleurs migrants
            when nl.code in ('2', '3', '5', '7') then 'AUTRE' --  Logements foyers pour personnes âgées, Logements foyers pour personnes handicapées, Logements foyers pour jeunes travailleurs, Logements foyers destinés à l'habitat inclusif
        end as nature_logement,
        coalesce(ir.indicevariation, 1.) as evolution
    from ecolo.ecolo_indiceredevance ir
        inner join ecolo.ecolo_valeurparamstatic vps on ir.annee_id = vps.id
        inner join ecolo.ecolo_naturelogement nl on ir.naturelogement_id = nl.id
) ir
                """
        )

        with transaction.atomic():
            for result in results:
                IndiceEvolutionLoyer.objects.update_or_create(
                    defaults=result,
                    date_debut=result["date_debut"],
                    date_fin=result["date_fin"],
                    nature_logement=result["nature_logement"],
                )
