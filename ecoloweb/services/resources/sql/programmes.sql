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
-- nature_logement                         varchar(25)              not null,
-- date_autorisation_hors_habitat_inclusif                        date,
-- date_convention_location                                       date,
-- date_residence_agrement                                        date,
-- date_residence_argement_gestionnaire_intermediation            date,
-- departement_residence_agrement                                 varchar(255),
-- departement_residence_argement_gestionnaire_intermediation     varchar(255),
-- ville_signature_residence_agrement_gestionnaire_intermediation varchar(255)



select
    cdg.id,
    cp.parent_id,
    pl.bailleur_id,
    c.entitecreatrice_id as administration_id,
    pl.code_postal,
    pl.ville,
    pl.adresse,
    c.libelle as nom,
    coalesce(pl.type_operation, 'SANSOBJET') as type_operation,
    pl.numero_galion,
    pl.date_achat,
    pl.date_achevement,
    pl.date_achevement_previsible,
    pl.surface_utile_totale,
    pl.code_insee_commune,
    pl.code_insee_departement,
    pl.code_insee_region,
    case
        when nl.code = '1' then 'LOGEMENTSORDINAIRES'
    end as nature_logement,
    cdg.datehistoriquedebut as date_achevement,
    coalesce(pl.datemisechantier, cdg.datehistoriquedebut) as cree_le,
    coalesce(pl.datemisechantier, cdg.datehistoriquedebut) as mis_a_jour_le
from ecolo.ecolo_conventiondonneesgenerales cdg
    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
    left join (
        select
            cdg.id,
            lag(cdg.id) over (partition by cdg.conventionapl_id order by a.numero nulls first) as parent_id
        from ecolo.ecolo_conventiondonneesgenerales cdg
            inner join ecolo.ecolo_avenant a on cdg.avenant_id = a.id
    ) cp on cp.id = cdg.id
    inner join ecolo.ecolo_naturelogement nl on cdg.naturelogement_id = nl.id and nl.code in ('1')
    inner join (
        select
            distinct on (pl.conventiondonneesgenerales_id, pl.typefinancement_id)
            pl.id,
            pl.conventiondonneesgenerales_id,
            pl.bailleurproprietaire_id as bailleur_id,
            pa.codepostal as code_postal,
            pl.datemisechantier,
            pl.surfaceutile as surface_utile_totale,
            pl.financementdate as date_achat,
            pl.datemiseservice as date_achevement,
            pl.datemiseservice as date_achevement_previsible,
            pa.ville,
            pa.ligne1||' '||pa.ligne2||' '||pa.ligne3||' '||pa.ligne4 as adresse,
            case
                when nop.libelle = 'Acquisition seule' then 'ACQUIS'
                when nop.libelle = 'Neuf ou construction' then 'NEUF'
                when nop.libelle = 'Acquisition/amélioration' then 'ACQUISAMELIORATION'
                when nop.libelle = 'Amélioration' then 'REHABILITATION'
                when nop.libelle = 'Parc existant' then 'USUFRUIT'
                else 'SANSOBJET'
            end as type_operation,
            ec.code as code_insee_commune,
            ed.codeinsee as code_insee_departement,
            er.codeinsee as code_insee_region,
            pl.financementreferencedossier as numero_galion
        from ecolo.ecolo_programmelogement pl
            left join ecolo.ecolo_programmeadresse pa on pl.id = pa.programmelogement_id
            left join ecolo.ecolo_valeurparamstatic nop on pl.natureoperation_id = nop.id
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
            inner join ecolo.ecolo_region er on ed.region_id = er.id
        order by pl.conventiondonneesgenerales_id, pl.typefinancement_id, pl.ordre
    ) pl on pl.conventiondonneesgenerales_id = cdg.id
where
    cdg.id = %s