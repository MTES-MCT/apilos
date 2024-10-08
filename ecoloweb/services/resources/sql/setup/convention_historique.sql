drop materialized view if exists ecolo.ecolo_conventionhistorique;

create materialized view ecolo.ecolo_conventionhistorique as
select
    ch.conventionapl_id||':'||ch.financement||':'||ch.numero as id,
    ch.id as conventiondonneesgenerales_id,
    ch.conventionapl_id,
    ch.avenant_id,
    ch.financement,
    ch.is_avenant,
    ch.numero,
    case
        when ch.parent_id is not null then ch.conventionapl_id||':'||ch.financement||':0'
    end as parent_id,
    cd.programme_ids,
    first_value(cd.departements[1]) over (partition by ch.conventionapl_id) as departement,
    row_number() over (partition by ch.conventionapl_id, ch.financement order by ch.numero desc) = 1 as is_last
from (
    -- convention historique (ch): restriction à l'itération de convention non avenant la plus récente (i.e. dont la
    -- valeur de `datehistorique` est la plus grande) suivie de tous les avenants qui suivent.
    -- Avec en plus déclinaison de cet historique pour tous les financements:
    -- * si un financement est apparu sur un avenant alors celui-ci devient la convention racine sur l'historique de ce
    --   financement
    -- * si au contraire un financement disparait en cours de route, les avenants suivants ne figurent pas dans son his-
    --   torique
    select
    c.conventiondonneesgenerales_id as id,
    c.conventionapl_id,
    c.avenant_id,
    pf.financement,
    c.numero > 0 as is_avenant,
    c.numero,
    case
        when c.numero > 0 then first_value(c.conventiondonneesgenerales_id) over (partition by c.conventionapl_id, pf.financement order by c.numero)
    end as parent_id
from (
    -- Refactorisation: désormais la convention racine est la convention instruite suivie de tous les avenants avec
    -- éventuellement une conventiondonnesgenerales s'ils en ont une sinon celle du parent. Le toute séparé en
    -- différents historiques par financement
    select
        case
            when c.conventiondonneesgenerales_id is not null then c.conventiondonneesgenerales_id
            else first_value(c.conventiondonneesgenerales_id) over (partition by c.conventionapl_id order by c.numero nulls first)
        end as conventiondonneesgenerales_id,
        c.conventionapl_id,
        c.avenant_id,
        c.numero
    from
        (
            select c.conventionapl_id, c.conventiondonneesgenerales_id, c.avenant_id, c.numero
            from (
                select distinct on (c.id) c.id as conventionapl_id, cdg.id as conventiondonneesgenerales_id, null::bigint as avenant_id, 0 as numero
                from ecolo.ecolo_conventiondonneesgenerales cdg
                    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
                    -- Exclusion des conventions annulées en instruction, donc obsolètes
                    inner join ecolo.ecolo_valeurparamstatic vps on vps.id = cdg.etatconvention_id and vps.code <> 'ANI'
                where cdg.avenant_id is null
                order by c.id, cdg.datehistoriquedebut desc
            ) c
            union all
            select a.conventionapl_id, cdg.id as conventiondonneesgenerales_id, a.id as avenant_id, a.numero
            from ecolo.ecolo_avenant a
                left join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.avenant_id = a.id
            where numero > 0
        ) c
        order by c.conventionapl_id, c.numero nulls first
    ) c
        inner join (
            select distinct on (pl.conventiondonneesgenerales_id, ff.code)
                pl.conventiondonneesgenerales_id,
                case
                    when tf.code in ('18', '22', '93') then 'SANS_FINANCEMENT'
                    else ff.code
                end as financement
            from ecolo.ecolo_programmelogement pl
                inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
                inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
        ) pf on pf.conventiondonneesgenerales_id = c.conventiondonneesgenerales_id
) ch
    inner join (
        -- convention details (cd): départements et bailleurs associés à la convention
        select
            pl.conventiondonneesgenerales_id,
            tf.financement,
            pg_catalog.array_agg(distinct(pl.id) ) as programme_ids,
            --pg_catalog.array_agg(distinct(ec.code)) as communes,
            pg_catalog.array_agg(distinct(ed.codeinsee)) as departements
            --pg_catalog.array_agg(distinct(pl.bailleurproprietaire_id)) as bailleurs
        from ecolo.ecolo_programmelogement pl
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
            inner join (
                select
                    tf.id,
                    case
                        when tf.code in ('18', '22', '93') then 'SANS_FINANCEMENT'
                        else ff.code
                    end as financement
                from ecolo.ecolo_typefinancement tf
                    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
            ) tf on pl.typefinancement_id = tf.id
        group by pl.conventiondonneesgenerales_id, tf.financement
        -- Exclusion des conventions multi, i.e. ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
        having count(distinct(ec.code)) = 1 and count(distinct(pl.bailleurproprietaire_id)) = 1
    ) cd on cd.conventiondonneesgenerales_id = ch.id and cd.financement = ch.financement
order by ch.conventionapl_id, ch.financement, ch.numero;

create unique index on ecolo.ecolo_conventionhistorique (id);