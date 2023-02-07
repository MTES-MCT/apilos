{% extends "_base_conventions.sql" %}

{% block from %}
    {{ block.super }}
    inner join (
        -- Historique de convention: toutes les itérations de la convention de la plus récente (toujours courante)
        -- jusqu'à la première non avenant incluse
        select distinct on (ch.conventionapl_id, ch.avenant_id) ch.*
        from (
            select *
            from ecolo.ecolo_conventiondonneesgenerales
            order by conventionapl_id, datehistoriquedebut desc
        ) ch
    ) ch on ch.id = cdg.id
{% endblock %}


{% block where %}
where
    -- On exclue les conventions ayant (au moins) un lot associé à plus d'un bailleur ou d'une commune
    not exists (
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
{% endblock %}
{% block order %}
-- order by cdg.conventionapl_id, cdg.datehistoriquedebut, a.numero nulls first
{% endblock %}
