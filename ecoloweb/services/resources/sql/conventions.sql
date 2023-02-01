-- Requête pour alimenter la table conventions_convention

-- fond_propre                        double precision
-- type1and2                          varchar(25)
-- avenant_type                       varchar(25)
select
    cdg.id||':'||pl.financement as id,
    case when
        lag(cdg.id) over (partition by cdg.conventionapl_id order by numero nulls first) is not null then
            lag(cdg.id) over (partition by cdg.conventionapl_id order by numero nulls first)||':'||pl.financement
    end as parent_id,
    cdg.id as programme_id,
    md5(cdg.id||'-'||pl.financement) as lot_id, -- Les lots d'un programme sont tous les logements partageant le même financement
    pl.financement as financement,
    c.noreglementaire as numero,
    case
        when cdg.dateannulation is not null then '8. Annulée en suivi'
        when cdg.datedemandedenonciation is not null then '7. Dénoncée'
        when cdg.dateresiliationprefet is not null then '6. Résiliée'
        when pec.code = 'INS' and c.noreglementaire is null then '2. Instruction requise'
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
    cdg.motifrefushypotheque as motif_refus_spf
from ecolo.ecolo_conventionapl c
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.id = cdg.conventionapl_id
    inner join ecolo.ecolo_valeurparamstatic pec on cdg.etatconvention_id = pec.id
    inner join ecolo.ecolo_naturelogement nl on cdg.naturelogement_id = nl.id
    inner join (
        select
            distinct on (pl.conventiondonneesgenerales_id, ff.code)
            pl.conventiondonneesgenerales_id,
            ff.code as financement,
            ff.id as financement_id,
            ed.codeinsee as departement
        from ecolo.ecolo_programmelogement  pl
            inner join ecolo.ecolo_commune ec on pl.commune_id = ec.id
            inner join ecolo.ecolo_departement ed on ec.departement_id = ed.id
            inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
            inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
    ) pl on pl.conventiondonneesgenerales_id = cdg.id
    left join ecolo.ecolo_avenant a on a.conventionprecedente_id = cdg.id
    left join ecolo.ecolo_conventiondonneesgenerales cdg2 on cdg2.avenant_id = a.id
where
    cdg.id = %s
    and pl.financement = %s
