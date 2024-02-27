# Generated by Django 4.2.9 on 2024-02-19 18:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("programmes", "0089_indiceevolutionloyer_departements"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DROP TRIGGER IF EXISTS search_vector_trigger_programme ON programmes_programme;
                DROP FUNCTION IF EXISTS search_vector_programme_func;

                CREATE TRIGGER search_vector_trigger_programme
                BEFORE INSERT OR UPDATE OF nom
                ON programmes_programme
                FOR EACH ROW EXECUTE PROCEDURE
                tsvector_update_trigger(
                    search_vector, 'pg_catalog.french', nom
                );

                UPDATE programmes_programme SET search_vector = NULL;
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS search_vector_trigger_programme ON programmes_programme;
                DROP FUNCTION IF EXISTS search_vector_programme_func;
            """,
        ),
    ]