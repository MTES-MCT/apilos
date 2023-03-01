-- Requête pour alimenter la table programmes_reference_cadastrale

select ic.id,
    ch.id as programme_id,
    ic.id,
    ic.section,
    -- le champs Parcelle d'Ecolo est "splitté" en autant de lignes qu'il y a de valeurs séparées par un caractère non alphanumérique
    ic.numero::int,
    pl.description as lieudit,
    ic.superficie,
    coalesce(pl.datemisechantier, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as cree_le,
    coalesce(pl.datemisechantier, cdg.datehistoriquedebut)::timestamp at time zone 'Europe/Paris' as mis_a_jour_le
from ecolo.ecolo_programmelogement pl
    inner join ecolo.ecolo_conventionhistorique ch on pl.conventiondonneesgenerales_id = ch.conventiondonneesgenerales_id and ch.programme_ids[1] = pl.id
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.id = ch.conventiondonneesgenerales_id
    inner join (
        select
            ic.id,
            ic.programmelogement_id,
            ic.section,
            -- le champs Parcelle d'Ecolo est "splitté" en autant de lignes qu'il y a de valeurs séparées par un caractère non alphanumérique
            unnest(regexp_split_to_array(ic.parcelle, '[^0-9]+')) as numero,
            ic.superficie
        from ecolo.ecolo_infocadastrale ic
    ) ic on ic.programmelogement_id = pl.id and trim(ic.numero) <> ''
where
    ch.id = %s
