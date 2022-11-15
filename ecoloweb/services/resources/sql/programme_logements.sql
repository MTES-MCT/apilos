-- Requête pour alimenter la table programmes_logement

-- Champs restants à mapper:
-- surface_annexes_retenue numeric(6, 2)
-- loyer_par_metre_carre   numeric(6, 2)
-- bailleur_id  FK(bailleur)  not null
-- lot_id   FK(programmes_lot) not null
select
    l.id,
    l.numerobatiment||' '||l.noescalier||' '||l.etage||' '||l.numerologement as designation,
    ptl.code as typologie,
    l.surfacehabitable::float as surface_habitable,
    l.surfaceannexe::float as surface_annexes,
    l.surfaceutile::float as surface_utile,
    l.coefficientmodulation as coefficient,
    l.montantloyer as loyer,
    l.datecreation as cree_le,
    l.datecreation as mis_a_jour_le,
    l.programmelogement_id as lot_id
from ecolo.ecolo_logement l
    inner join ecolo.ecolo_programmelogement pl on l.programmelogement_id = pl.id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on pl.conventiondonneesgenerales_id = cdg.id and cdg.avenant_id is null
    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
    inner join ecolo.ecolo_valeurparamstatic ptl on l.typelogement_id = ptl.id
where
    pl.id = %s