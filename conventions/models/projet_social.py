from django.db import models

from . import Convention


class ProjetSocial(models.Model):
    convention = models.OneToOneField(
        Convention,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="projet_social",
    )
    publics_accueillis = models.TextField(blank=True)
    actions_relogement_social = models.TextField(blank=True)
    conditions_specifiques_accueil = models.TextField(blank=True)
    conditions_admission = models.TextField(blank=True)
    duree_maximale_accueil_mois = models.PositiveIntegerField(null=True)
    conditions_renouvellement_accueil = models.TextField(blank=True)
    modalites_attribution = models.TextField(blank=True)
    actions_caractere_social = models.TextField(blank=True)
    action_insertion_par_logement = models.TextField(blank=True)
    projet_relogement = models.TextField(blank=True)
