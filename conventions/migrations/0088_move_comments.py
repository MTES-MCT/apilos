# Generated by Django 4.2.13 on 2024-08-19 09:08

from django.db import migrations


def move_adresse_commentaire(apps, schema_editor):
    Comment = apps.get_model("comments", "Comment")
    comments = Comment.objects.filter(nom_objet="adresse")
    for comment in comments:
        convention = comment.convention
        comment.nom_objet = "convention"
        comment.champ_objet = "adresse"
        comment.uuid_objet = convention.uuid
        comment.save()
    prog_comments = Comment.objects.filter(nom_objet="programme", champ_objet="adresse")
    for comment in prog_comments:
        convention = comment.convention
        comment.nom_objet = "convention"
        comment.champ_objet = "adresse"
        comment.uuid_objet = convention.uuid
        comment.save()


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0087_alter_convention_financement"),
    ]

    operations = [
        migrations.RunPython(move_adresse_commentaire, migrations.RunPython.noop)
    ]
