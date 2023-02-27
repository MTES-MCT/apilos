{% extends "_base_conventions.sql" %}


{% block where %}
where
    vps.code <> 'ANI' -- Conventions annulées en instruction donc obsolètes
    and ch.departement = %s
{% endblock %}

{% block order %}
-- On trie les conventions par ordre de précédence afin que les conventions racines (& leur programme / lot)
-- soient créées AVANT leurs avenants
order by ch.conventionapl_id, ch.financement, ch.numero nulls first
{% endblock %}
