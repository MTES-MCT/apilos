-- Requête pour alimenter la table programmes_reference_cadastrale

-- Champs restants à mapper:
-- cree_le       timestamp with time zone not null,
-- mis_a_jour_le timestamp with time zone not null

select ic.id,
    pl.conventiondonneesgenerales_id as programme_id,
    pl.bailleurproprietaire_id as bailleur_id,
    ic.id,
    ic.section,
    -- le champs Parcelle d'Ecolo est "splitté" en autant de lignes qu'il y a de valeurs séparées par un caractère non alphanumérique
    unnest(regexp_split_to_array(ic.parcelle, '[^0-9]+')) as raw_numero,
    pl.description as lieudit,
    ic.superficie
from ecolo.ecolo_infocadastrale ic
    inner join ecolo.ecolo_programmelogement pl on ic.programmelogement_id = pl.id
where
    pl.conventiondonneesgenerales_id = %s
