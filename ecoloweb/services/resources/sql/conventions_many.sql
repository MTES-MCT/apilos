select
    -- Only select id at this step
    cdg.id||':'||pl.financement as id,
    case when
        cp.parent_id is not null and cp.parent_id <> cdg.id then
            cp.parent_id||':'||pl.financement
    end as parent_id,
    -- Les avenants sont initialisés avec un type 'commentaires' dont la valeur est un résumé des altérations
    -- déclarées depuis Ecoloweb
    ('{"files": {}, "text": "Avenant issu d''Ecoloweb:\r\n\r\n'||ta.detail_avenant||'"}')::json as comments,
    cdg.id as programme_id,
    -- Les lots d'un programme sont tous les logements partageant le même financement
    md5(cdg.id||'-'||pl.financement) as lot_id,
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
from ecolo.ecolo_conventiondonneesgenerales cdg
    left join (
        select
            cdg.id,
            lag(cdg.id) over (partition by cdg.conventionapl_id order by a.numero nulls first) as parent_id
        from ecolo.ecolo_conventiondonneesgenerales cdg
            inner join ecolo.ecolo_avenant a on cdg.avenant_id = a.id
    ) cp on cp.id = cdg.id
    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
    left join ecolo.ecolo_avenant a on cdg.avenant_id = a.id
    left join (
        select ta.avenant_id,
            string_agg(pat.libelle, '\r\n') as detail_avenant
        from ecolo.ecolo_avenant_typeavenant ta
            left join ecolo.ecolo_valeurparamstatic pat on ta.typeavenant_id = pat.id
        group by ta.avenant_id
    ) ta on ta.avenant_id = cdg.avenant_id
    inner join ecolo.ecolo_valeurparamstatic pec on cdg.etatconvention_id = pec.id
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
    nl.code = '1' -- Seulement les "Logements ordinaires" pour le moment
    -- On exclue les conventions ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
    and not exists (
        select
            pl2.conventiondonneesgenerales_id
        from ecolo.ecolo_programmelogement pl2
            inner join ecolo.ecolo_conventiondonneesgenerales cdg2 on cdg2.id = pl2.conventiondonneesgenerales_id
            inner join ecolo.ecolo_typefinancement tf2 on pl2.typefinancement_id = tf2.id
            inner join ecolo.ecolo_famillefinancement ff2 on tf2.famillefinancement_id = ff2.id
        where cdg2.id = cdg.id
        group by pl2.conventiondonneesgenerales_id, ff2.libelle
        having count(distinct(pl2.commune_id)) > 1 or count(distinct(pl2.bailleurproprietaire_id)) > 1
    )
    and pl.departement = %s
order by cdg.conventionapl_id, cdg.datehistoriquedebut, a.numero nulls first

