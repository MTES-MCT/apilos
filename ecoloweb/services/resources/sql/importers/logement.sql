-- Requête pour alimenter la table programmes_logement

select
    l.id,
    ch.id as lot_id,
    coalesce(l.numerobatiment||' '||l.noescalier||' '||l.etage||' '||l.numerologement, '') as designation,
    case
        when ptl.code in ('ST1', 'T1') then 'T1'
        when ptl.code in ('T1B', 'T1P') then 'T1bis'
        else ptl.code -- T2+ are exactly the same
    end as typologie,
    coalesce(round(cast(l.surfacecorrigee as numeric), 2),  as surface_corrigee,
    round(cast(l.surfaceutile as numeric), 2) as surface_utile,
    round(cast(l.surfacehabitable as numeric), 2) as surface_habitable,
    round(cast(l.surfaceannexe as numeric), 2) as surface_annexes,
    round(cast(l.surfaceannexe as numeric), 2) as surface_annexes_retenue,
    l.coefficientmodulation as coeficient,
    l.montantloyer as loyer,
    pl.montantplafondloyerindinitial as loyer_par_metre_carre,
    to_timestamp(l.datecreation / 1000)::timestamp at time zone 'Europe/Paris' as cree_le,
    to_timestamp(l.datecreation / 1000)::timestamp at time zone 'Europe/Paris' as mis_a_jour_le
from ecolo.ecolo_logement l
    inner join ecolo.ecolo_valeurparamstatic ptl on l.typelogement_id = ptl.id
    inner join ecolo.ecolo_programmelogement pl on l.programmelogement_id = pl.id
    inner join ecolo.ecolo_conventionhistorique ch on pl.conventiondonneesgenerales_id = ch.conventiondonneesgenerales_id
where
    ch.id = %s