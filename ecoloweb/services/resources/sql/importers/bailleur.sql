-- Requête pour alimenter la table bailleurs_bailleur:

-- signataire_fonction          varchar(255),
-- signataire_date_deliberation date,
-- operation_exceptionnelle     text,
-- capital_social               double precision
select
    b.id,
    case
        when b.raisonsociale = 'ANAH' then 'Personne(s) physique(s)'
        else b.raisonsociale
    end as nom,
    case
        when b.raisonsociale = 'ANAH' then 'XXXXXXXXXXXXXX'
        -- Bailleurs privés (codepersonne > codesiret > codesiren)
        when snb.code = '611' and (trim(b.codepersonne) <> '') is true then trim(b.codepersonne)
        when snb.code = '611' and (trim(b.codepersonne) <> '') is not true and (trim(b.codesiret) <> '') is true then trim(b.codesiret)
        when snb.code = '611' and (trim(b.codepersonne) <> '') is not true and (trim(b.codesiret) <> '') is not true and (trim(b.codesiren) <> '') is true then trim(b.codesiren)
        -- Autres bailleurs (codesiret > codesiren > codepersonne)
        when (trim(b.codesiret) <> '') is true then trim(b.codesiret)
        when (trim(b.codesiret) <> '') is not true and (trim(b.codesiren) <> '') is true then trim(b.codesiren)
        when (trim(b.codesiret) <> '') is not true and (trim(b.codesiren) <> '') is not true and (trim(b.codepersonne) <> '') is true then trim(b.codepersonne)
        -- Dernier recours: la raison sociale privée de ses caractères non alpha numériques, en majuscules et limitée à
        -- 14 caractères (format SIRET)
        else substring(upper(regexp_replace(b.raisonsociale, '[^a-zA-Z0-9]+', '', 'g')), 1, 14)
    end as codesiret,
    cb.noms_contacts as signataire_nom,
    case
        when b.raisonsociale = 'ANAH' or snb.code = '611' then 'Bailleurs privés'
        when snb.code = '210' then 'SEM'
        when snb.code in ('110', '112', '114', '120', '130', '140') then 'HLM'
        else 'Autres bailleurs sociaux non HLM'
    end as nature_bailleur,
    case
        when b.raisonsociale = 'ANAH' then 'ANAH'
        when snb.code = '110' then 'COOPERATIVE_HLM_SCIC'
        when snb.code = '112' then 'COOPERATIVE_HLM_SCIC'
        when snb.code = '114' then 'OFFICE_PUBLIC_HLM'
        when snb.code = '120' then 'SA_HLM_ESH'
        when snb.code = '130' then 'COOPERATIVE_HLM_SCIC'
        when snb.code = '140' then 'SACI_CAP'
        when snb.code = '210' then 'SEM_EPL'
        when snb.code = '312' then 'COMMUNE'
        when snb.code = '314' then 'ETC_PUBLIQUE_LOCAL'
        when snb.code = '316' then 'ETS_HOSTIPATIERS_PRIVES'
        when snb.code = '320' then 'EPCI'
        when snb.code = '321' then 'FONDATION_HLM'
        when snb.code = '322' then 'ASSOCIATIONS'
        when snb.code = '323' then 'ASSOCIATIONS'
        when snb.code = '324' then 'ASSOCIATIONS'
        when snb.code = '325' then 'ETC_PUBLIQUE_LOCAL'
        when snb.code = '326' then 'COMMERCIALES'
        when snb.code = '327' then 'ASSOCIATIONS'
        when snb.code = '328' then 'FRONCIERE_LOGEMENT'
        when snb.code = '329' then 'ASSOCIATIONS'
        when snb.code = '330' then 'GIP'
        when snb.code = '331' then 'FONDATION'
        when snb.code = '332' then 'MUTUELLE'
        when snb.code = '333' then 'EPCI'
        when snb.code = '334' then 'DEPARTEMENT'
        when snb.code = '335' then 'ETC_PUBLIQUE_LOCAL'
        when snb.code = '336' then 'PACT_ARIM'
        when snb.code = '337' then 'CROUS'
        when snb.code = '338' then 'DRE_DDE_CETE_AC_PREF'
            when snb.code = '611' then 'PARTICULIERS'
        else 'NONRENSEIGNE'
    end as sous_nature_bailleur,
    b.datemodif::timestamp at time zone 'Europe/Paris' as cree_le,
    b.datemodif::timestamp at time zone 'Europe/Paris' as mis_a_jour_le,
    ab.ligne1||' '||ab.ligne2||' '||ab.ligne3||' '||ab.ligne4 as adresse,
    ab.codepostal as code_postal,
    ab.ville as ville
from ecolo.ecolo_bailleur b
    left join ecolo.ecolo_adressebailleur ab on b.adresse_id = ab.id
    left join ecolo.ecolo_departement ed on b.departement_id = ed.id
    inner join ecolo.ecolo_sousnaturebailleur snb on b.sousnaturebailleur_id = snb.id
    left join (
        select
            cb.bailleur_id, string_agg(vps.libelle||' '||cb.prenom||' '||cb.nom, ', ') as noms_contacts
        from ecolo.ecolo_contactbailleur cb
            inner join ecolo.ecolo_valeurparamstatic vps on cb.civilite_id = vps.id
        group by cb.bailleur_id
    ) cb on cb.bailleur_id = b.id
where
    b.id = %s
