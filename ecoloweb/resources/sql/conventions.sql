-- Requête pour alimenter la table conventions_convention

-- numero                             varchar(255),
-- date_fin_conventionnement          date,
-- financement                        varchar(25)              not null,
-- soumis_le                          timestamp with time zone,
-- valide_le                          timestamp with time zone,
-- cree_le                            timestamp with time zone not null,
-- mis_a_jour_le                      timestamp with time zone not null,
-- bailleur_id FK(bailleur) not null
-- lot_id FK(programme_lot) not null
-- programme_id FK(programme) not null
-- comments                           text
-- fond_propre                        double precision
-- statut                             varchar(25)              not null
-- premiere_soumission_le             timestamp with time zone
-- type1and2                          varchar(25)
-- type2_lgts_concernes_option1       boolean                  not null
-- type2_lgts_concernes_option2       boolean                  not null
-- type2_lgts_concernes_option3       boolean                  not null
-- type2_lgts_concernes_option4       boolean                  not null
-- type2_lgts_concernes_option5       boolean                  not null
-- type2_lgts_concernes_option6       boolean                  not null
-- type2_lgts_concernes_option7       boolean                  not null
-- type2_lgts_concernes_option8       boolean                  not null
-- donnees_validees                   text
-- nom_fichier_signe                  varchar(255)
-- date_resiliation                   date
-- televersement_convention_signee_le timestamp with time zone
-- avenant_type                       varchar(25)
-- parent_id                          FK(conventions) i.e. les avenants
-- cree_par_id                        bigint
-- signataire_date_deliberation       date
-- signataire_fonction                varchar(255)
-- signataire_nom                     varchar(255)
select
    c.id,
    c.noordre as numero
from ecolo.ecolo_conventionapl c
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.id = cdg.conventionapl_id
where
    cdg.avenant_id is null -- exclude avenant related conventions
{% if max_row %}
order by random()
limit {{ max_row }}
{% endif %}
