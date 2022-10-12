                 -- Requête pour alimenter la table programmes_programme
select
    cdg.id,
    c.libelle,
    coalesce(p.type_operation, 'SANSOBJET') as type_operation,
    p.numero_galion
from ecolo.ecolo_conventiondonneesgenerales cdg
    inner join ecolo.ecolo_conventionapl c on cdg.conventionapl_id = c.id
    inner join (
        select
            distinct on (pl.conventiondonneesgenerales_id)
            pl.conventiondonneesgenerales_id,
            -- All rows from ecolo_programmelogement tied to the same conventiondonneesgenerales_id
            -- always have the same ecolo_valeurparamstatic attached
            case
                when nop.libelle = 'Acquisition seule' then 'ACQUIS'
                when nop.libelle = 'Neuf ou construction' then 'NEUF'
                when nop.libelle = 'Acquisition/amélioration' then 'ACQUISAMELIORATION'
                when nop.libelle = 'Amélioration' then 'REHABILITATION'
                when nop.libelle = 'Parc existant' then 'USUFRUIT'
                else 'SANSOBJET'
            end as type_operation,
            pl.financementreferencedossier as numero_galion
        from ecolo.ecolo_programmelogement pl
            left join ecolo.ecolo_valeurparamstatic nop on pl.natureoperation_id = nop.id
        order by pl.conventiondonneesgenerales_id, pl.ordre
    ) p on p.conventiondonneesgenerales_id = cdg.id
where cdg.avenant_id is null
{% if max_row %}
order by random()
limit {{ max_row }}
{% endif %}
