-- Requête pour alimenter la table conventions_convention

-- financement                        varchar(25)              not null,
-- lot_id FK(programme_lot) not null
-- programme_id FK(programme) not null
-- comments                           text
-- fond_propre                        double precision
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
    pb.bailleur_id,
    cdg.id as programme_id,
    md5(cdg.id||'-'||ff.code) as lot_id, -- Les lots d'un programme sont tous les logements partageant le même financement
    c.noreglementaire as numero,
    case
        when pec.code = 'INS' then '2. Instruction requise'
        when pec.code = 'ANI' then '3. Corrections requises' -- Abandonnée en instruction
        when pec.code = 'OPP' then '5. Signée'
        when pec.code = 'RES' then '6. Résiliée'
        when pec.code = 'DEN' then '7. Dénoncée'
        when pec.code = 'ANS' then '8. Annulée en suivi'
    end as statut,
    cdg.datehistoriquefin as date_fin_conventionnement,
    -- Financement
    c.datedepot::timestamp at time zone '{{ timezone }}' as soumis_le,
    ev.date_validation::timestamp at time zone '{{ timezone }}' as valide_le,
    c.datesaisie::timestamp at time zone '{{ timezone }}' as cree_le,
    c.datemodification::timestamp at time zone '{{ timezone }}' as mis_a_jour_le,
    eps.date_premiere_soumission::timestamp at time zone '{{ timezone }}' as premiere_soumission_le,
    er.date_resiliation as date_resiliation
from ecolo.ecolo_conventionapl c
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.id = cdg.conventionapl_id
    inner join ecolo.ecolo_programmelogement pl on pl.conventiondonneesgenerales_id = cdg.id
    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    inner join ecolo.ecolo_entitegest eg on c.entitecreatrice_id = eg.id
    inner join ecolo.ecolo_entitegestadresse aa on eg.adresse_id = aa.id
    inner join ecolo.ecolo_departement ed on starts_with(aa.codepostal, ed.codeinsee)
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
    inner join ecolo.ecolo_valeurparamstatic pec on cdg.etatconvention_id = pec.id and pec.subtype = 'ECO' -- Etat de la convention
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
    {% if departements %}
    and ed.codeinsee in ({{ departements|safeseq|join:',' }})
    {% endif %}
