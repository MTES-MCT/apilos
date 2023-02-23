--typologie         varchar(35)              not null
--nb_stationnements integer                  not null
--loyer             numeric(6, 2)            not null

select
    ch.id as lot_id,
    'GARAGE_AERIEN' as typologie,
    sum(ea.nombre) as nb_stationnements,
    sum(ea.montantloyerinitial) as loyer,
    min(ea.datecreation) as cree_le,
    min(ea.datecreation) as mis_a_jour_le
from ecolo.ecolo_programmelogement pl
    inner join ecolo.ecolo_annexe ea on pl.id = ea.programmelogement_id
    inner join ecolo.ecolo_valeurparamstatic ev on ea.typeannexe_id = ev.id and ev.subtype = 'TAN' and ev.code in ('10', '20', '80')
    inner join ecolo.ecolo_conventionhistorique ch on pl.conventiondonneesgenerales_id = ch.conventiondonneesgenerales_id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.id = ch.conventiondonneesgenerales_id
where
    ch.id = %s
group by ch.id, pl.conventiondonneesgenerales_id