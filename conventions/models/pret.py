import uuid
from typing import Any

from django.db import models
from django.forms import model_to_dict

from conventions.models import Convention
from conventions.models.choices import Preteur


class Pret(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention", on_delete=models.CASCADE, null=False, related_name="prets"
    )
    preteur = models.CharField(
        max_length=25,
        choices=Preteur.choices,
        default=Preteur.AUTRE,
    )
    autre = models.CharField(null=True, blank=True, max_length=255)
    date_octroi = models.DateField(null=True, blank=True)
    numero = models.CharField(null=True, blank=True, max_length=255)
    duree = models.IntegerField(null=True, blank=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    # Needed to import xlsx files
    import_mapping = {
        "Numéro\n(caractères alphanuméric)": numero,
        "Date d'octroi\n(format dd/mm/yyyy)": date_octroi,
        "Durée\n(en années)": duree,
        "Montant\n(en €)": montant,
        "Prêteur\n(choisir dans la liste déroulante)": preteur,
        "Préciser l'identité du préteur si vous avez sélectionné 'Autre'": autre,
    }
    sheet_name = "Financements"

    def __str__(self):
        return f"{self.convention} ({self.preteur})"

    def clone(self, convention: Convention, **kwargs: dict[str, Any]) -> "Pret":
        pret_fields = (
            model_to_dict(
                self,
                exclude=[
                    "uuid",
                    "id",
                    "cree_le",
                    "mis_a_jour_le",
                ],
            )
            | {"convention": convention}
            | kwargs
        )
        return Pret.objects.create(**pret_fields)

    def _get_preteur(self):
        return self.get_preteur_display()

    p = property(_get_preteur)

    def _get_autre(self):
        return self.autre

    a = property(_get_autre)

    def _get_date_octroi(self):
        return self.date_octroi

    do = property(_get_date_octroi)

    def _get_numero(self):
        return self.numero

    n = property(_get_numero)

    def _get_duree(self):
        return self.duree

    d = property(_get_duree)

    def _get_montant(self):
        return self.montant

    m = property(_get_montant)

    def p_full(self):
        return self.get_preteur_display().replace(
            "CDC", "Caisse de Dépôts et Consignation"
        )

    def preteur_display(self):
        if self.preteur == Preteur.AUTRE:
            return self.autre
        return self.p_full()
