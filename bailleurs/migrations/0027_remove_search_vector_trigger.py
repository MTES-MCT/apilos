from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bailleurs", "0026_remove_bailleur_search_vector_bailleur_idx_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DROP TRIGGER IF EXISTS search_vector_trigger_bailleur ON bailleurs_bailleur;
                DROP FUNCTION IF EXISTS search_vector_bailleur_func;
            """
        )
    ]
