{% extends "_base_conventions.sql" %}


{% block where %}
where ch.departement = %s
{% endblock %}

{% block order %}
-- On trie les conventions par ordre de précédence afin que les conventions racines (& leur programme / lot)
-- soient créées AVANT leurs avenants
order by ch.conventionapl_id, ch.numero nulls first
{% endblock %}
