-- Requête pour alimenter la table programmes_lot

-- financement varchar(25)  not null
-- type_habitat   enum('INDIVIDUEL', 'COLLECTIF', 'MIXTE')
-- cree_le timestamp with time zone not null
-- mis_a_jour_le  timestamp with time zone not null
-- bailleur_id  FK(bailleurs_bailleur) not null
-- programme_id FK(programmes_programme) not null
-- annexe_ateliers boolean not null
-- annexe_balcons boolean not null
-- annexe_caves boolean not null
-- annexe_celliers              boolean                  not null,
-- annexe_combles               boolean                  not null,
-- annexe_loggias               boolean                  not null,
-- annexe_remises               boolean                  not null,
-- annexe_resserres             boolean                  not null,
-- annexe_sechoirs              boolean                  not null,
-- annexe_soussols              boolean                  not null,
-- annexe_terrasses             boolean                  not null,
-- edd_classique                text,
-- edd_volumetrique             text,
-- type_habitat                 varchar(25)              not null,
-- lgts_mixite_sociale_negocies integer                  not null,
-- loyer_derogatoire            numeric(6, 2),
-- parent_id   FK(programmes_lot)

select
    pl.id,
    logementsnombretotal as nb_logements,
    case
        when coalesce(pl.logementsnombreindtotal, 0) > 0 and coalesce(pl.logementsnombrecoltotal, 0) > 0 then 'MIXTE'
        when coalesce(pl.logementsnombreindtotal, 0) > 0 then 'INDIVIDUEL'
        else 'COLLECTIF'
    end as type_habitat
from ecolo.ecolo_programmelogement pl
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on pl.conventiondonneesgenerales_id = cdg.id
    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
where
    cdg.avenant_id is null
    and pl.logementsnombretotal > 0
{% if max_row %}
order by random()
limit {{ max_row }}
{% endif %}