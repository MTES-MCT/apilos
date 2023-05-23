-- Requête pour alimenter la table programmes_programme

-- Champs restants à mapper:
-- nb_locaux_commerciaux                integer,
-- nb_bureaux                           integer,
-- vendeur                              text,
-- acquereur                            text,
-- date_acte_notarie                    date,
-- permis_construire                    varchar(255),
-- reference_notaire                    text,
-- reference_publication_acte           text,
-- annee_gestion_programmation          integer,
-- surface_utile_totale                 numeric(8, 2),
-- autres_locaux_hors_convention        text,
-- acte_de_propriete                    text,
-- edd_volumetrique                     text,
-- certificat_adressage                 text,
-- edd_classique                        text,
-- mention_publication_edd_classique    text,
-- mention_publication_edd_volumetrique text,
-- reference_cadastrale                 text,
-- zone_123                             varchar(25),
-- zone_abc                             varchar(25),
-- date_achevement_compile              date,
-- effet_relatif                        text
-- date_autorisation_hors_habitat_inclusif                        date,
-- date_convention_location                                       date,
-- date_residence_agrement                                        date,
-- date_residence_argement_gestionnaire_intermediation            date,
-- departement_residence_agrement                                 varchar(255),
-- departement_residence_argement_gestionnaire_intermediation     varchar(255),
-- ville_signature_residence_agrement_gestionnaire_intermediation varchar(255)

select
    ch.conventionapl_id||':'||ch.numero,
    chp.conventionapl_id||':'||chp.numero as parent_id,
    pl.bailleurproprietaire_id as bailleur_id,
    c.entitecreatrice_id as administration_id,
    coalesce(cp.codepostal, pa.codepostal, ec.code) as code_postal,
    ec.libelle as ville,
    pa.ligne1||' '||pa.ligne2||' '||pa.ligne3||' '||pa.ligne4 as adresse,
    case
        when (pl.description <> '') is true then pl.description
        when (pa.ligne1 <> '') is true then pa.ligne1||' - '||coalesce(pl.logementsnombretotal, coalesce(pl.logementsnombreindtotal, 0) + coalesce(pl.logementsnombrecoltotal, 0))||' - '||ch.financement
        when (pa.ligne2 <> '') is true then pa.ligne2||' - '||coalesce(pl.logementsnombretotal, coalesce(pl.logementsnombreindtotal, 0) + coalesce(pl.logementsnombrecoltotal, 0))||' - '||ch.financement
        when (pa.ligne3 <> '') is true then pa.ligne3||' - '||coalesce(pl.logementsnombretotal, coalesce(pl.logementsnombreindtotal, 0) + coalesce(pl.logementsnombrecoltotal, 0))||' - '||ch.financement
        else ec.libelle||' - '||coalesce(pl.logementsnombretotal, coalesce(pl.logementsnombreindtotal, 0) + coalesce(pl.logementsnombrecoltotal, 0))||' - '||ch.financement
    end as nom,
    case
        when nop.libelle = 'Acquisition seule' then 'ACQUIS'
        when nop.libelle = 'Neuf ou construction' then 'NEUF'
        when nop.libelle = 'Acquisition/amélioration' then 'ACQUISAMELIORATION'
        when nop.libelle = 'Amélioration' then 'REHABILITATION'
        when nop.libelle = 'Parc existant' then 'USUFRUIT'
        else 'SANSOBJET'
    end as type_operation,
    pl.financementreferencedossier as numero_galion,
    pl.financementdate as date_achat,
    pl.datemiseservice as date_achevement,
    pl.datemiseservice as date_achevement_previsible,
    pl.surfaceutile as surface_utile_totale,
    pl.surfacecorrigee as surface_corrigee_totale,
    ec.code as code_insee_commune,
    ed.codeinsee as code_insee_departement,
    er.codeinsee as code_insee_region,
    case
        when nl.code = '1' then 'LOGEMENTSORDINAIRES'
        when nl.code = '6' then 'RESISDENCESOCIALE'
        else 'AUTRE'
    end as nature_logement,
    cdg.datehistoriquedebut as date_achevement,
    coalesce(pl.datemisechantier, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as cree_le,
    coalesce(pl.datemisechantier, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as mis_a_jour_le
from ecolo.ecolo_conventionhistorique ch
    -- Vérification qu'il existe bien une ligne pour le parent de parent_id (au cas où exclure les changements de financement)
    left join ecolo.ecolo_conventionhistorique chp on chp.id = ch.parent_id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.id = ch.conventiondonneesgenerales_id
    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
    left join ecolo.ecolo_avenant a on cdg.avenant_id = a.id
    inner join ecolo.ecolo_naturelogement nl on cdg.naturelogement_id = nl.id
    inner join ecolo.ecolo_programmelogement pl on  pl.id = ch.programme_ids[1]
    left join ecolo.ecolo_programmeadresse pa on pl.id = pa.programmelogement_id
    left join ecolo.ecolo_valeurparamstatic nop on pl.natureoperation_id = nop.id
    inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
    left join ecolo.ecolo_codepostal cp on ec.code = cp.codeinsee
    inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
    inner join ecolo.ecolo_region er on ed.region_id = er.id
where
    (ch.conventionapl_id||':'||ch.numero) = %s
