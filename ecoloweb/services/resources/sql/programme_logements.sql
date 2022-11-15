-- Requête pour alimenter la table programmes_logement

-- Champs restants à mapper:
-- surface_annexes_retenue numeric(6, 2)
-- loyer_par_metre_carre   numeric(6, 2)
-- bailleur_id  FK(bailleur)  not null
-- lot_id   FK(programmes_lot) not null
select
    l.id,
    md5(pl.conventiondonneesgenerales_id||'-'||ff.code) as lot_id,
    pl.conventiondonneesgenerales_id as programme_id,
    l.numerobatiment||' '||l.noescalier||' '||l.etage||' '||l.numerologement as designation,
    ptl.code as typologie,
    l.surfacehabitable::float as surface_habitable,
    l.surfaceannexe::float as surface_annexes,
    l.surfaceutile::float as surface_utile,
    l.coefficientmodulation as coefficient,
    l.montantloyer as loyer,
    l.datecreation as cree_le,
    l.datecreation as mis_a_jour_le
from ecolo.ecolo_logement l
    inner join ecolo.ecolo_programmelogement pl on l.programmelogement_id = pl.id
    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    inner join ecolo.ecolo_valeurparamstatic ptl on l.typelogement_id = ptl.id
where
    md5(pl.conventiondonneesgenerales_id||'-'||ff.code) = %s