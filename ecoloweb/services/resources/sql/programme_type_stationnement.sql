--typologie         varchar(35)              not null
--nb_stationnements integer                  not null
--loyer             numeric(6, 2)            not null

select
    pl.conventiondonneesgenerales_id||':'||ff.code as lot_id,
    'GARAGE_AERIEN' as typologie,
    sum(ea.nombre) as nb_stationnements,
    sum(ea.montantloyerinitial) as loyer,
    min(ea.datecreation) as cree_le,
    min(ea.datecreation) as mis_a_jour_le
from ecolo.ecolo_programmelogement pl
    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    inner join ecolo.ecolo_annexe ea on pl.id = ea.programmelogement_id
    inner join ecolo.ecolo_valeurparamstatic ev on ea.typeannexe_id = ev.id and ev.subtype = 'TAN' and ev.code in ('10', '20', '80')
where
    pl.conventiondonneesgenerales_id = %s
    and ff.code = %s
group by pl.conventiondonneesgenerales_id, ff.code