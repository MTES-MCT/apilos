{% extends "_base_conventions.sql" %}

{% block where %}
where
    cdg.id = %s
    and pl.financement = %s
{% endblock %}
