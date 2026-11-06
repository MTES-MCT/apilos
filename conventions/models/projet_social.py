from django.db import models

from . import Convention


class ProjetSocial(models.Model):
    convention = models.OneToOneField(
        Convention,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="projet_social",
    )
    publics_accueillis = models.TextField()
    actions_relogement_social = models.TextField()
    conditions_specifiques_accueil = models.TextField(blank=True)
    conditions_admission = models.TextField()
    duree_maximale_accueil_mois = models.PositiveIntegerField()
    conditions_renouvellement_accueil = models.TextField()
    modalites_attribution = models.TextField()
    actions_caractere_social = models.TextField()
    action_insertion_par_logement = models.TextField()
    projet_relogement = models.TextField(blank=True)
