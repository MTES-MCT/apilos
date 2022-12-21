-- Requête pour alimenter la table conventions_convention

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
    c.id||':'||pl.financement as id,
    cdg.id as programme_id,
    md5(cdg.id||'-'||pl.financement) as lot_id, -- Les lots d'un programme sont tous les logements partageant le même financement
    pl.financement as financement,
    c.noreglementaire as numero,
    case
        when cdg.dateannulation is not null then '8. Annulée en suivi'
        when cdg.datedemandedenonciation is not null then '7. Dénoncée'
        when cdg.dateresiliationprefet is not null then '6. Résiliée'
        when pec.code = 'INS' and c.noreglementaire is null then '2. Instruction requise'
        -- Manquent les états 9. Renouvelée, 10. Expirée
        else '5. Signée'
    end as statut,
    cdg.datehistoriquefin as date_fin_conventionnement,
    -- Financement
    c.datedepot::timestamp at time zone 'Europe/Paris' as soumis_le,
    cdg.datesignatureentitegest::timestamp at time zone 'Europe/Paris' as valide_le,
    c.datesaisie::timestamp at time zone 'Europe/Paris' as cree_le,
    c.datemodification::timestamp at time zone 'Europe/Paris' as mis_a_jour_le,
    cdg.datesignatureentitegest::timestamp at time zone 'Europe/Paris' as premiere_soumission_le,
    cdg.dateresiliationprefet as date_resiliation
from ecolo.ecolo_conventionapl c
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.id = cdg.conventionapl_id and cdg.avenant_id is null
    inner join ecolo.ecolo_valeurparamstatic pec on cdg.etatconvention_id = pec.id and pec.subtype = 'ECO' -- Etat de la convention
    inner join ecolo.ecolo_naturelogement nl on cdg.naturelogement_id = nl.id
    inner join (
        select
            distinct on (pl.conventiondonneesgenerales_id, ff.code)
            pl.conventiondonneesgenerales_id,
            ff.code as financement,
            ed.codeinsee as departement
        from ecolo.ecolo_programmelogement  pl
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
            inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
            inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    ) pl on pl.conventiondonneesgenerales_id = cdg.id
where
    nl.code = '1' -- Seulement les "Logements ordinaires"
    and pl.departement = %s
    -- On exclue les conventions ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
    and not exists (
        select
            pl2.conventiondonneesgenerales_id
        from ecolo.ecolo_programmelogement pl2
            inner join ecolo.ecolo_conventiondonneesgenerales cdg2 on cdg2.id = pl2.conventiondonneesgenerales_id and cdg2.avenant_id is null
            inner join ecolo.ecolo_typefinancement tf2 on pl2.typefinancement_id = tf2.id
            inner join ecolo.ecolo_famillefinancement ff2 on tf2.famillefinancement_id = ff2.id
        where cdg2.id = cdg.id
        group by pl2.conventiondonneesgenerales_id, ff2.libelle
        having count(distinct(pl2.commune_id)) > 1 or count(distinct(pl2.bailleurproprietaire_id)) > 1
    )
order by cdg.datehistoriquedebut desc, cdg.datesignatureentitegest desc nulls last

