-- Requête pour alimenter la table programmes_logement

select
    l.id,
    md5(pl.conventiondonneesgenerales_id||'-'||ff.code) as lot_id,
    coalesce(l.numerobatiment||' '||l.noescalier||' '||l.etage||' '||l.numerologement, '') as designation,
    case
        when ptl.code in ('ST1', 'T1') then 'T1'
        when ptl.code in ('T1B', 'T1P') then 'T1bis'
        else ptl.code -- T2+ are exactly the same
    end as typologie,
    l.surfacehabitable::float as surface_habitable,
    l.surfaceannexe::float as surface_annexes,
    l.surfaceannexe::float as surface_annexes_retenue,
    l.surfaceutile::float as surface_utile,
    l.coefficientmodulation as coeficient,
    l.montantloyer as loyer,
    case
        when l.montantloyer is null then null
        when l.montantloyer = 0 then 0
        when l.surfacecorrigee is not null and l.surfacecorrigee <> 0 then l.montantloyer / l.surfacecorrigee
        when l.surfaceutile is not null and l.surfaceutile <> 0 then l.montantloyer / l.surfaceutile
        when l.surfacehabitable is not null and l.surfacehabitable <> 0 then l.montantloyer / l.surfacehabitable
    end as loyer_par_metre_carre,
    l.datecreation as cree_le,
    l.datecreation as mis_a_jour_le
from ecolo.ecolo_logement l
    inner join ecolo.ecolo_programmelogement pl on l.programmelogement_id = pl.id
    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    inner join ecolo.ecolo_valeurparamstatic ptl on l.typelogement_id = ptl.id
where
    md5(pl.conventiondonneesgenerales_id||'-'||ff.code) = %s