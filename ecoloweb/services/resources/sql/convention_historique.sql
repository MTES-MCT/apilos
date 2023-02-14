select
    ch.id,
    ch.conventionapl_id,
    ch.financement,
    ch.is_avenant and ch.rank > 1 as is_avenant,
    ch.rank - 1 as numero,
    case when
        ch.parent_id is not null and ch.parent_id <> ch.id and ch.rank > 1 then ch.parent_id
    end as parent_id,
    d.codeinsee as departement
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
        -- Récupération du département associé à la convention
        select distinct on (pl.conventiondonneesgenerales_id) pl.conventiondonneesgenerales_id, ed.codeinsee
        from ecolo.ecolo_programmelogement pl
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
    ) d on d.conventiondonneesgenerales_id = ch.id
where
    -- Exclusion des conventions multi, i.e. ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
    not exists (
        select
            pl2.conventiondonneesgenerales_id
        from ecolo.ecolo_programmelogement pl2
            inner join ecolo.ecolo_conventiondonneesgenerales cdg2 on cdg2.id = pl2.conventiondonneesgenerales_id
            inner join ecolo.ecolo_typefinancement tf2 on pl2.typefinancement_id = tf2.id
            inner join ecolo.ecolo_famillefinancement ff2 on tf2.famillefinancement_id = ff2.id
        where cdg2.id = ch.id
        group by pl2.conventiondonneesgenerales_id, ff2.libelle
        having count(distinct(pl2.commune_id)) > 1 or count(distinct(pl2.bailleurproprietaire_id)) > 1
    )
order by ch.conventionapl_id, ch.financement, ch.datehistoriquedebut