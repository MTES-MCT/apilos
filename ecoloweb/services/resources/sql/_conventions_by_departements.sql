-- Recursive query to ensure a parent convention is always fetched before its children
with recursive convention_parents (id, parent_id) as (
  select c.id, null::bigint as parent_id
  from ecolo.ecolo_conventionapl c
        inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.conventioncourante_id = cdg.id
  where cdg.avenant_id is null
  union all
  select c.id, cdg.avenant_id as parent_id
  from ecolo.ecolo_conventionapl c
      inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.conventioncourante_id = cdg.id
      inner join convention_parents on convention_parents.id = cdg.avenant_id
)
select
    -- Only select id at this step
    c.id||':'||pl.financement||':'||cdg.datehistoriquedebut as id
from convention_parents cp
    inner join ecolo.ecolo_conventionapl c on cp.id = c.id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.id = cdg.conventionapl_id and cdg.avenant_id is null
    inner join ecolo.ecolo_valeurparamstatic pec on cdg.etatconvention_id = pec.id and pec.subtype = 'ECO' -- Etat de la convention
    inner join ecolo.ecolo_naturelogement nl on cdg.naturelogement_id = nl.id
    inner join (
        select
            distinct on (pl.conventiondonneesgenerales_id, ff.code)
            pl.conventiondonneesgenerales_id,
            ff.code as financement,
            ed.codeinsee as departement
        from ecolo.ecolo_programmelogement  pl
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
            inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
            inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    ) pl on pl.conventiondonneesgenerales_id = cdg.id
where
    nl.code = '1' -- Seulement les "Logements ordinaires"
    -- On exclue les conventions ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
    and not exists (
        select
            pl2.conventiondonneesgenerales_id
        from ecolo.ecolo_programmelogement pl2
            inner join ecolo.ecolo_conventiondonneesgenerales cdg2 on cdg2.id = pl2.conventiondonneesgenerales_id and cdg2.avenant_id is null
            inner join ecolo.ecolo_typefinancement tf2 on pl2.typefinancement_id = tf2.id
            inner join ecolo.ecolo_famillefinancement ff2 on tf2.famillefinancement_id = ff2.id
        where cdg2.id = cdg.id
        group by pl2.conventiondonneesgenerales_id, ff2.libelle
        having count(distinct(pl2.commune_id)) > 1 or count(distinct(pl2.bailleurproprietaire_id)) > 1
    )
    and pl.departement = %s

