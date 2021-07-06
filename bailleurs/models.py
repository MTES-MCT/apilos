import uuid

from django.db import models
from django.utils import timezone
from django.urls import reverse

class Bailleur(models.Model):
    class Meta:
        permissions = (('can_edit_bailleur', "Créer ou mettre à jour un bailleur"),)
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    siret = models.CharField(max_length=14)
    capital_social = models.CharField(max_length=255)
    siege = models.CharField(max_length=255)
    dg_nom = models.CharField(max_length=255)
    dg_fonction = models.CharField(max_length=255)
    dg_date_deliberation = models.DateField()
    operation_exceptionnelle = models.TextField()

    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

#    def get_absolute_url(self):
#        return reverse('bailleur:bailleur-detail', args=[str(self.uuid)])
