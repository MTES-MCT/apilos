{% extends "_base_conventions.sql" %}

{% block where %}
where
    ch.id = %s
{% endblock %}
