-- Requête pour alimenter la table programmes_lot

-- Champs restants à mapper:
-- annexe_ateliers boolean not null
-- annexe_balcons boolean not null
-- annexe_celliers              boolean                  not null,
-- annexe_combles               boolean                  not null,
-- annexe_loggias               boolean                  not null,
-- annexe_resserres             boolean                  not null,
-- annexe_sechoirs              boolean                  not null,
-- annexe_soussols              boolean                  not null,
-- edd_classique                text,
-- edd_volumetrique             text,
-- lgts_mixite_sociale_negocies integer                  not null,
-- parent_id   FK(programmes_lot) dans le cas d'un avenant seulement ?
-- surface_habitable_totale               numeric(7, 2),
-- foyer_residence_dependance             text,
-- foyer_residence_locaux_hors_convention text,
-- foyer_residence_nb_garage_parking      integer

select
    ch.id as id, -- Les lots d'un programme sont tous les logements partageant le même financement
    chp.id as parent_id,
    ch.id as programme_id,
    coalesce(pl.financementdate::timestamp at time zone 'Europe/Paris', now()) as cree_le,
    coalesce(pl.financementdate::timestamp at time zone 'Europe/Paris', now()) as mis_a_jour_le,
    ch.financement,
    coalesce(pl.logementsnombretotal, coalesce(pl.logementsnombreindtotal, 0) + coalesce(pl.logementsnombrecoltotal, 0)) as nb_logements,
    case
        when pl.logementsnombreindtotal > 0 and (pl.logementsnombrecoltotal is null or pl.logementsnombrecoltotal = 0) then 'INDIVIDUEL'
        when pl.logementsnombrecoltotal > 0 and (pl.logementsnombreindtotal is null or pl.logementsnombreindtotal = 0) then 'COLLECTIF'
        else 'MIXTE'
    end as type_habitat,
    case
        when coalesce(pl.logementsnombreindtotal, 0) > 0 and coalesce(pl.logementsnombrecoltotal, 0) > 0 then 'MIXTE'
        when coalesce(pl.logementsnombreindtotal, 0) > 0 then 'INDIVIDUEL'
        else 'COLLECTIF'
    end as type_habitat,
    ap1.id is not null as annexe_caves,
    ap2.id is not null as annexe_terrasses,
    ap3.id is not null as annexe_remises,
    case
        when pl.estderogationloyer and coalesce(pl.logementsnombreindtotal, 0) > 0 then pl.montantplafondloyerindinitial
        when pl.estderogationloyer and coalesce(pl.logementsnombrecoltotal, 0) > 0 then pl.montantplafondloyercolinitial
    end as loyer_derogatoire,
    round(cast(pl.surfacehabitable as numeric), 2) as surface_habitable_totale,
    case when nl.code <> '1' then a4.nombre end as foyer_residence_nb_garage_parking
from ecolo.ecolo_programmelogement pl
    inner join ecolo.ecolo_conventionhistorique ch on pl.conventiondonneesgenerales_id = ch.conventiondonneesgenerales_id
    -- Vérification qu'il existe bien une ligne pour le parent de parent_id (au cas où exclure les changements de financement)
    left join ecolo.ecolo_conventionhistorique chp on chp.id = ch.parent_id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.id = ch.conventiondonneesgenerales_id
    left join ecolo.ecolo_avenant a on cdg.avenant_id = a.id
    -- Nature logement
    inner join ecolo.ecolo_naturelogement nl on cdg.naturelogement_id = nl.id
    -- Annexes
    left join ecolo.ecolo_annexe a1 on a1.programmelogement_id = pl.id
    left join ecolo.ecolo_valeurparamstatic ap1 on a1.typeannexe_id = ap1.id and ap1.subtype = 'TAN' and ap1.code = '7' -- Cave
    left join ecolo.ecolo_annexe a2 on a2.programmelogement_id = pl.id
    left join ecolo.ecolo_valeurparamstatic ap2 on a2.typeannexe_id = ap2.id and ap2.subtype = 'TAN' and ap2.code = '5' -- Terrasse
    left join ecolo.ecolo_annexe a3 on a3.programmelogement_id = pl.id
    left join ecolo.ecolo_valeurparamstatic ap3 on a3.typeannexe_id = ap3.id and ap3.subtype = 'TAN' and ap3.code = '8' -- Box
    left join ecolo.ecolo_annexe a4 on a4.programmelogement_id = pl.id
    left join ecolo.ecolo_valeurparamstatic ap4 on a4.typeannexe_id = ap4.id and ap4.subtype = 'TAN' and ap3.code = '2' -- Parking
where
    ch.id = %s
