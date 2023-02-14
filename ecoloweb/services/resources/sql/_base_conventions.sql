select
    ch.id||':'||ch.financement as id,
    ch.parent_id||':'||ch.financement as parent_id,
    -- Les avenants sont initialisés avec un type 'commentaires' dont la valeur est un résumé des altérations
    -- déclarées depuis Ecoloweb
    ('{"files": {}, "text": "Avenant issu d''Ecoloweb:\r\n\r\n'||ta.detail_avenant||'"}')::json as commentaires,
    cdg.id||':'||ch.financement as programme_id,
    -- Les lots d'un programme sont tous les logements partageant le même financement
    ch.id||':'||ch.financement as lot_id,
    ch.financement as financement,
    case
        when
            ch.is_avenant then ch.numero::text
        else c.noreglementaire
    end as numero,
    case
        when cdg.dateannulation is not null then '8. Annulée en suivi'
        when cdg.datedemandedenonciation is not null then '7. Dénoncée'
        when cdg.dateresiliationprefet is not null then '6. Résiliée'
        when vps.code = 'INS' and c.noreglementaire is null then '2. Instruction requise'
        else '5. Signée'
    end as statut,
    cdg.datehistoriquefin as date_fin_conventionnement,
    -- Financement
    c.datedepot::timestamp at time zone 'Europe/Paris' as soumis_le,
     -- The latest non null signature date is the one considered as accurate
    greatest(
        cdg.datesignatureentitegest::timestamp at time zone 'Europe/Paris',
        cdg.datesignaturebailleur::timestamp at time zone 'Europe/Paris',
        cdg.datesignatureprefet::timestamp at time zone 'Europe/Paris'
    ) as valide_le,
    c.datesaisie::timestamp at time zone 'Europe/Paris' as cree_le,
    c.datemodification::timestamp at time zone 'Europe/Paris' as mis_a_jour_le,
    cdg.datesignatureentitegest::timestamp at time zone 'Europe/Paris' as premiere_soumission_le,
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
-- Conventions à leur dernier état connu et actualisé, pour éviter les doublons de convention
{% block from %}
from ecolo.ecolo_conventionapl c
    inner join ecolo.ecolo_conventionhistorique ch on ch.conventionapl_id = c.id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.id = ch.id
    left join ecolo.ecolo_avenant a on cdg.avenant_id = a.id
    inner join ecolo.ecolo_valeurparamstatic vps on vps.id = cdg.etatconvention_id
    -- Détail des modifications, en cas d'avenant
    left join (
        select ta.avenant_id,
            string_agg(pat.libelle, '\r\n') as detail_avenant
        from ecolo.ecolo_avenant_typeavenant ta
            left join ecolo.ecolo_valeurparamstatic pat on ta.typeavenant_id = pat.id
        group by ta.avenant_id
    ) ta on ta.avenant_id = a.id
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
{% endblock %}
{% block where %}
{% endblock %}
{% block order %}
{% endblock %}
