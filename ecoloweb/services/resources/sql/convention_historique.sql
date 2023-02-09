select
    cdg.id,
    cdg.conventionapl_id,
    cdg.financement,
    cdg.avenant_id is not null as is_avenant,
    case
        when
            cdg.avenant_id is not null
        then rank() over (partition by cdg.conventionapl_id, cdg.financement order by cdg.datehistoriquedebut) - 1
    end as numero,
    case
        when first_value(cdg.id) over (partition by cdg.conventionapl_id order by cdg.datehistoriquedebut) <> id
        then first_value(cdg.id) over (partition by cdg.conventionapl_id order by cdg.datehistoriquedebut)
    end as parent_id,
    d.codeinsee as departement
from (
    select
        -- Restriction aux itérations de conventions les plus récentes, à savoir la dernière convention non avenant
        -- suivie de tous ses avenants
        distinct on (cdg.conventionapl_id, cdg.financement, cdg.avenant_id)
        cdg.*
    from (
        select cdg.*, cf.financement
        from ecolo.ecolo_conventiondonneesgenerales cdg
            -- cf : convention financements
            -- Récupération des financements de la convention
            inner join (
                select distinct on (pl.conventiondonneesgenerales_id, ff.code) pl.conventiondonneesgenerales_id, ff.code as financement
                from ecolo.ecolo_programmelogement pl
                    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
                    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
            ) cf on cf.conventiondonneesgenerales_id = cdg.id
            -- fv : financements valides
            -- Intersection avec les financements de la convention racine (pour éliminer les avenants ayant des
            -- financements de programme autres (cas des changements / ajouts de financement en cours de route)
            inner join (
                select distinct on (cdg.conventionapl_id, ff.code) cdg.conventionapl_id, ff.code as financement
                from ecolo.ecolo_conventiondonneesgenerales cdg
                    inner join ecolo.ecolo_programmelogement pl on pl.conventiondonneesgenerales_id = cdg.id
                    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
                    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
                where cdg.avenant_id is null
                order by cdg.conventionapl_id, ff.code, cdg.datehistoriquedebut desc
            ) fv on cdg.conventionapl_id = fv.conventionapl_id and cf.financement = fv.financement
        order by cdg.conventionapl_id, cf.financement, cdg.datehistoriquedebut desc
    ) cdg
) cdg
    inner join (
        -- Récupération du département associé à la convention
        select distinct on (pl.conventiondonneesgenerales_id) pl.conventiondonneesgenerales_id, ed.codeinsee
        from ecolo.ecolo_programmelogement pl
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
    ) d on d.conventiondonneesgenerales_id = cdg.id
where
    -- Exclusion des conventions multi, i.e. ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
    not exists (
        select
            pl2.conventiondonneesgenerales_id
        from ecolo.ecolo_programmelogement pl2
            inner join ecolo.ecolo_conventiondonneesgenerales cdg2 on cdg2.id = pl2.conventiondonneesgenerales_id
            inner join ecolo.ecolo_typefinancement tf2 on pl2.typefinancement_id = tf2.id
            inner join ecolo.ecolo_famillefinancement ff2 on tf2.famillefinancement_id = ff2.id
        where cdg2.id = cdg.id
        group by pl2.conventiondonneesgenerales_id, ff2.libelle
        having count(distinct(pl2.commune_id)) > 1 or count(distinct(pl2.bailleurproprietaire_id)) > 1
    )
order by cdg.conventionapl_id, cdg.datehistoriquedebut