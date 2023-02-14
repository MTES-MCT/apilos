select
    ch.id,
    ch.conventionapl_id,
    ch.financement,
    ch.is_avenant and ch.rank > 1 as is_avenant,
    ch.rank - 1 as numero,
    case when
        ch.parent_id is not null and ch.parent_id <> ch.id and ch.rank > 1 then ch.parent_id
    end as parent_id,
    cd.programme_ids,
    --cd.communes,
    cd.departements[1] as departement
    --cd.bailleurs
from (
    -- convention historique (ch): restriction à l'itération de convention non avenant la plus récente (i.e. dont la
    -- valeur de `datehistorique` est la plus grande) suivie de tous les avenants qui suivent.
    -- Avec en plus déclinaison de cet historique pour tous les financements:
    -- * si un financement est apparu sur un avenant alors celui-ci devient la convention racine sur l'historique de ce
    --   financement
    -- * si au contraire un financement disparait en cours de route, les avenants suivants ne figurent pas dans son his-
    --   torique
    select
        cdg.id,
        cdg.conventionapl_id,
        cdg.datehistoriquedebut,
        cdg.avenant_id,
        cdg.avenant_id is not null as is_avenant,
        ff.code as financement,
        rank() over (partition by cdg.conventionapl_id, ff.code order by cdg.datehistoriquedebut) as rank,
        first_value(cdg.id) over (partition by cdg.conventionapl_id, ff.code order by cdg.datehistoriquedebut) as parent_id
    from ecolo.ecolo_conventiondonneesgenerales cdg
        -- convention courante (cc): pour chaque conventionapl_id la conventiondonneesgenerales non avenant la plus récente
        inner join (
            select distinct on (cdg.conventionapl_id) cdg.id, cdg.datehistoriquedebut, cdg.conventionapl_id
            from ecolo.ecolo_conventiondonneesgenerales cdg
                where cdg.avenant_id is null
            order by cdg.conventionapl_id,  cdg.datehistoriquedebut desc
        ) cc on cc.conventionapl_id = cdg.conventionapl_id and cdg.datehistoriquedebut >= cc.datehistoriquedebut
        inner join ecolo.ecolo_programmelogement pl on cdg.id = pl.conventiondonneesgenerales_id
        inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
        inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
) ch
    inner join (
        -- convention details (cd): départements et bailleurs associés à la convention
        select
            pl.conventiondonneesgenerales_id,
            ff.code as financement,
            pg_catalog.array_agg(distinct(pl.id) ) as programme_ids,
            --pg_catalog.array_agg(distinct(ec.code)) as communes,
            pg_catalog.array_agg(distinct(ed.codeinsee)) as departements
            --pg_catalog.array_agg(distinct(pl.bailleurproprietaire_id)) as bailleurs
        from ecolo.ecolo_programmelogement pl
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
            inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
            inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
        group by pl.conventiondonneesgenerales_id, ff.code
        -- Exclusion des conventions multi, i.e. ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
        having count(distinct(ec.code)) = 1 and count(distinct(pl.bailleurproprietaire_id)) = 1
    ) cd on cd.conventiondonneesgenerales_id = ch.id and cd.financement = ch.financement
order by ch.conventionapl_id, ch.financement, ch.datehistoriquedebut