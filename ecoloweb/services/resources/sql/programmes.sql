-- Requête pour alimenter la table programmes_programme

-- Champs restants à mapper:
-- code_postal                          varchar(10),
-- ville                                varchar(255),
-- adresse                              text,
-- anru                                 boolean                  not null,
-- nb_locaux_commerciaux                integer,
-- nb_bureaux                           integer,
-- vendeur                              text,
-- acquereur                            text,
-- date_acte_notarie                    date,
-- cree_le                              timestamp with time zone not null,
-- mis_a_jour_le                        timestamp with time zone not null,
-- date_achat                           date,
-- date_achevement                      date,
-- date_achevement_previsible           date,
-- permis_construire                    varchar(255),
-- reference_notaire                    text,
-- reference_publication_acte           text,
-- annee_gestion_programmation          integer,
-- surface_utile_totale                 numeric(8, 2),
-- administration_id                    integer
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
-- effet_relatif                        text,
-- code_insee_commune                   varchar(10),
-- code_insee_departement               varchar(10),
-- code_insee_region                    varchar(10),
-- nature_logement                      varchar(25)              not null,
-- parent_id                            integer

select
    cdg.id,
    pb.bailleur_id,
    c.libelle as nom,
    coalesce(p.type_operation, 'SANSOBJET') as type_operation,
    p.numero_galion
from ecolo.ecolo_conventiondonneesgenerales cdg
    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
    inner join (
        -- Sur Ecolo il peut y avoir un bailleur gestionnaire *par logement*, aussi on attribue à la convention le
        -- bailleur majoritaire
        select
            pl.conventiondonneesgenerales_id,
            pl.bailleurgestionnaire_id as bailleur_id
        from ecolo.ecolo_programmelogement pl
            inner join ecolo.ecolo_bailleur b on pl.bailleurgestionnaire_id = b.id
        group by pl.conventiondonneesgenerales_id, pl.bailleurgestionnaire_id
        order by count(distinct(b.id)) desc
    ) pb on pb.conventiondonneesgenerales_id = cdg.id
    inner join (
        select
            distinct on (pl.conventiondonneesgenerales_id)
            pl.conventiondonneesgenerales_id,
            -- All rows from ecolo_programmelogement tied to the same conventiondonneesgenerales_id
            -- always have the same ecolo_valeurparamstatic attached
            case
                when nop.libelle = 'Acquisition seule' then 'ACQUIS'
                when nop.libelle = 'Neuf ou construction' then 'NEUF'
                when nop.libelle = 'Acquisition/amélioration' then 'ACQUISAMELIORATION'
                when nop.libelle = 'Amélioration' then 'REHABILITATION'
                when nop.libelle = 'Parc existant' then 'USUFRUIT'
                else 'SANSOBJET'
            end as type_operation,
            pl.financementreferencedossier as numero_galion
        from ecolo.ecolo_programmelogement pl
            left join ecolo.ecolo_valeurparamstatic nop on pl.natureoperation_id = nop.id
        order by pl.conventiondonneesgenerales_id, pl.ordre
    ) p on p.conventiondonneesgenerales_id = cdg.id
where
    cdg.avenant_id is null
    and pb.bailleur_id is not null
    {% if pk %}
    and cdg.id = {{ pk }}
    {% endif %}