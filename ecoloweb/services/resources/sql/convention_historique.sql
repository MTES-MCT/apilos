select
    cdg.id,
    cdg.conventionapl_id,
    cdg.avenant_id is not null as is_avenant,
    case
        when
            cdg.avenant_id is not null
        then rank() over (partition by cdg.conventionapl_id order by cdg.datehistoriquedebut) - 1
    end as numero,
    case
        when first_value(cdg.id) over (partition by cdg.conventionapl_id order by cdg.datehistoriquedebut) <> id
        then first_value(cdg.id) over (partition by cdg.conventionapl_id order by cdg.datehistoriquedebut)
    end as parent_id,
    d.codeinsee as departement
from (
    select
        distinct on (cdg.conventionapl_id, cdg.avenant_id)
        cdg.*
    from (
        select *
        from ecolo.ecolo_conventiondonneesgenerales
        order by conventionapl_id, datehistoriquedebut desc
    ) cdg
) cdg
    inner join (
        -- Récupération du département associé à la convention
        select distinct on (pl.conventiondonneesgenerales_id) pl.conventiondonneesgenerales_id, ed.codeinsee
        from ecolo_programmelogement pl
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