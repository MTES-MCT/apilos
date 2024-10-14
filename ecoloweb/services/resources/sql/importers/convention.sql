select
    ch.id as id,
    chp.id as parent_id,
    ch.conventionapl_id||':'||ch.numero as programme_id,
    -- Les lots d'un programme sont tous les logements partageant le même financement
    ch.id as lot_id,
    ch.financement as financement,
    case
        when
            ch.is_avenant then ch.numero::text
        else c.noreglementaire
    end as numero,
    case
        -- On se base sur l'état déclaré dans Ecolo
        when vps.code in ('ANS', 'ANI') then '8. Annulée en suivi'
        when vps.code = 'DEN' then '7. Dénoncée'
        when vps.code = 'RES' then '6. Résiliée'
        -- Convention en instruction si état = 'INS' ET aucune date de signature
        when vps.code = 'INS' and coalesce(a.datesignatureprefet, cdg.datesignatureprefet, cdg.datesignatureentitegest) is null then '2. Instruction requise'
        else '5. Signée'
    end as statut,
    -- Dates
    cdg.datehistoriquefin as date_fin_conventionnement,
    c.datedepot::timestamp at time zone 'Europe/Paris' as soumis_le,
    coalesce(a.datesignatureprefet, cdg.datesignatureprefet, cdg.datesignatureentitegest, c.datedepot, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as televersement_convention_signee_le,
    coalesce(a.datesignatureprefet, cdg.datesignatureprefet, cdg.datesignatureentitegest, c.datedepot, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as valide_le,
    coalesce(c.datesaisie, c.datedepot, a.datesignatureprefet, cdg.datesignatureprefet, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as cree_le,
    coalesce(c.datemodification, a.datesignatureprefet, cdg.datesignatureprefet, c.datesaisie, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as mis_a_jour_le,
    coalesce(c.datesaisie, c.datedepot, a.datesignatureprefet)::timestamp at time zone 'Europe/Paris' as premiere_soumission_le,
    cdg.dateresiliationprefet as date_resiliation,
    cdg.datepublication as date_publication_spf,
    cdg.referencepublication as reference_spf,
    cdg.datepublication as date_envoi_spf,
    cdg.daterefushypotheque as date_refus_spf,
    cdg.motifrefushypotheque as motif_refus_spf,
    -- Résidences et foyers
    b.raisonsociale||'( '||coalesce(b.codesiret, b.codepersonne)||')' as gestionnaire,
    cb.noms_contacts as gestionnaire_signataire_nom,
    nl.code = '2' as attribution_agees_autonomie,
    nl.code = '2' as attribution_agees_autre,
    case when nl.code = '2' then 'Non renseigné (Ecoloweb)' end as attribution_agees_autre_detail,
    nl.code = '2' as attribution_agees_desorientees,
    nl.code = '2' as attribution_agees_ephad,
    nl.code = '2' as attribution_agees_petite_unite,
    nl.code = '3' as attribution_handicapes_autre,
    case when nl.code = '3' then 'Non renseigné (Ecoloweb)' end as attribution_handicapes_autre_detail,
    nl.code = '3' as attribution_handicapes_foyer,
    nl.code = '3' as attribution_handicapes_foyer_de_vie,
    nl.code = '3' as attribution_handicapes_foyer_medicalise,
    case when nl.code = '7' then 'Non renseigné (Ecoloweb)' end as attribution_inclusif_activites,
    case when nl.code = '7' then 'Non renseigné (Ecoloweb)' end as attribution_inclusif_conditions_admission,
    case when nl.code = '7' then 'Non renseigné (Ecoloweb)' end as attribution_inclusif_conditions_specifiques,
    case when nl.code = '7' then 'Non renseigné (Ecoloweb)' end as attribution_inclusif_modalites_attribution,
    case when nl.code = '7' then 'Non renseigné (Ecoloweb)' end as attribution_inclusif_partenariats,
    case when nl.code in ('2', '3', '4', '5', '7') then 'Non renseigné (Ecoloweb)' end as attribution_modalites_choix_personnes,
    case when nl.code in ('2', '3', '4', '5', '7') then 'Non renseigné (Ecoloweb)' end as attribution_modalites_reservations,
    case when nl.code in ('2', '3', '4', '5', '7') then 'Non renseigné (Ecoloweb)' end as attribution_prestations_facultatives,
    case when nl.code in ('2', '3', '4', '5', '7') then 'Non renseigné (Ecoloweb)' end as attribution_prestations_integrees,
    case when nl.code in ('2', '3', '4', '5', '7') then pl.reservationprefnombre end as attribution_reservation_prefectorale,
    case when nl.code <> '1' and nop.code = '80' then true else false end as foyer_residence_variante_1,
    case when nl.code <> '1' and nop.code = '5' then true else false end as foyer_residence_variante_2,
    case when nl.code <> '1' and nop.code = '5' then 'Non renseigné (Ecoloweb)' end as foyer_residence_variante_2_travaux,
    case when nl.code <> '1' and nop.code = '1' then true else false end as foyer_residence_variante_3,
    nl.code = '6' as attribution_pension_de_famille,
    nl.code = '6' as attribution_residence_accueil,
    nl.code in ('4', '5', '6') as attribution_residence_sociale_ordinaire
from ecolo.ecolo_conventionhistorique ch
    inner join ecolo.ecolo_conventionapl c on ch.conventionapl_id = c.id
    -- Vérification qu'il existe bien une ligne pour le parent de parent_id (au cas où exclure les changements de financement)
    left join ecolo.ecolo_conventionhistorique chp on chp.id = ch.parent_id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.id = ch.conventiondonneesgenerales_id
    left join ecolo.ecolo_avenant a on ch.avenant_id = a.id
    inner join ecolo.ecolo_valeurparamstatic vps on vps.id = cdg.etatconvention_id
    inner join ecolo.ecolo_naturelogement nl on cdg.naturelogement_id = nl.id
    inner join ecolo.ecolo_programmelogement pl on ch.programme_ids[1] = pl.id
    inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
    inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    left join ecolo.ecolo_valeurparamstatic nop on pl.natureoperation_id = nop.id
    left join ecolo.ecolo_bailleur b on pl.bailleurgestionnaire_id = b.id
    left join (
        select
            cb.bailleur_id,
            string_agg(vps.libelle||' '||cb.prenom||' '||cb.nom, ', ') as noms_contacts
        from ecolo.ecolo_contactbailleur cb
            inner join ecolo.ecolo_valeurparamstatic vps on cb.civilite_id = vps.id
        group by cb.bailleur_id
    ) cb on cb.bailleur_id = b.id
where
    ch.id = %s
