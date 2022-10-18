-- Requête pour alimenter la table conventions_convention

-- financement                        varchar(25)              not null,
-- bailleur_id FK(bailleur) not null
-- lot_id FK(programme_lot) not null
-- programme_id FK(programme) not null
-- comments                           text
-- fond_propre                        double precision
-- statut                             varchar(25)
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
-- televersement_convention_signee_le timestamp with time zone
-- avenant_type                       varchar(25)
-- parent_id                          FK(conventions) i.e. les avenants
-- cree_par_id                        bigint
-- signataire_fonction                varchar(255)
-- signataire_nom                     varchar(255)
select
    c.id,
    c.noreglementaire as numero,
    c.datedepot as soumis_le,
    ev.date_validation as valide_le,
    cdg.datehistoriquefin as date_fin_conventionnement,
    c.datesaisie as cree_le,
    c.datemodification as mis_a_jour_le,
    eps.date_premiere_soumission as premiere_soumission_le,
    er.date_resiliation as date_resiliation
from ecolo.ecolo_conventionapl c
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.id = cdg.conventionapl_id
    left join (
        select
            distinct on (e.conventionapl_id)
            e.conventionapl_id as convention_id,
            e.date as date_premiere_soumission
        from ecolo.ecolo_evenement e
            inner join ecolo.ecolo_valeurparamstatic ev on e.typeevenement_id = ev.id and ev.code = '1'
        order by e.conventionapl_id, e.date
    ) eps on eps.convention_id = c.id -- Évènement de résiliation
    left join (
        select
            distinct on (e.conventionapl_id)
            e.conventionapl_id as convention_id,
            e.date as date_resiliation
        from ecolo.ecolo_evenement e
            inner join ecolo.ecolo_valeurparamstatic ev on e.typeevenement_id = ev.id and ev.code = '22'
        order by e.conventionapl_id, e.date
    ) er on er.convention_id = c.id -- Évènement de résiliation
    left join (
        select
            distinct on (e.conventionapl_id)
            e.conventionapl_id as convention_id,
            e.date as date_validation
        from ecolo.ecolo_evenement e
            inner join ecolo.ecolo_valeurparamstatic ev on e.typeevenement_id = ev.id and ev.code = '13'
        order by e.conventionapl_id, e.date
    ) ev on ev.convention_id = c.id -- Évènement de résiliation
where
    cdg.avenant_id is null -- exclude avenant related conventions
{% if max_row %}
order by random()
limit {{ max_row }}
{% endif %}
