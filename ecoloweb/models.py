from typing import Optional

from django.db import models
from django.db.models import Model
from django.apps import apps


class EcoloReference(models.Model):
    """
    L'entité EcoloReference a pour but de maintenir un catalogue des équiva-
    lences entre les entités dans la base de données Ecoloweb et les modèles
    APiLos.

    Afin qu'aucune donnée provenant de la base Ecoloweb ne soit importée 2 fois,
    on marquera la référence via ce modèle.

    Les requêtes se feront donc _uniquement_ pour retrouver dans la base APiLos
    l'instance dont le modèle correspond à `apilos_model` (selon l'appellation
    officielle Django: `app_label`.`object_name`) et l'`id` externe, i.e. dans
    la base Ecolo, a pour valeur `ecolo_id`. D'où la déclaration des indexes
    d'_unicité_.

    Étant donné que cette entité pourrait potentiellement être reliée à
    plein d'autres, on opte de ne garder ici qu'un id multiple, mais forcément
    unique. Pour retrouver l'entité APiLos associée il faudra donc faire une
    seconde requête sur le modèle idoine.

    Par ailleurs le choix de centraliser sur une seule table de l'application
    `ecoloweb` repose aussi sur la volonté de scinder les informations propres
    à Ecolo du reste d'APiLos. L'import des données d'Ecoloweb n'étant pas voué
    à rester il sera plus facile de nettoyer le code associé en procédant ainsi.
    """

    class Meta:
        unique_together = ("apilos_model", "ecolo_id")

    id = models.AutoField(primary_key=True)
    apilos_model = models.CharField(max_length=64, null=False)
    ecolo_id = models.TextField(null=False, max_length=32)
    apilos_id = models.IntegerField(null=False)
    departement = models.CharField(max_length=3, null=False, default=None)
    importe_le = models.DateField(null=True)
    est_supprime = models.BooleanField(null=False, default=False)

    def _get_model(self):
        app_label, model_name = self.apilos_model.split(".")
        return apps.get_model(app_label, model_name)

    def resolve(self) -> Optional[Model]:
        return self._get_model().objects.filter(pk=self.apilos_id).first()

    def update(self, data: dict):
        return self._get_model().objects.filter(pk=self.apilos_id).update(**data)

    @classmethod
    def get_instance_model_name(cls, instance: Model) -> str:
        return cls.get_class_model_name(instance.__class__)

    @classmethod
    def get_class_model_name(cls, clazz) -> str:
        return f"{clazz._meta.app_label}.{clazz._meta.object_name}"

    def marquer_supprime(self):
        self.est_supprime = True
        self.save(update_fields=["est_supprime"])
