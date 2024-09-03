import logging

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from apilos_settings.models import Departement
from programmes.models.models import Lot, Programme

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Programme)
def compute_numero_operation_for_search(sender, instance, *args, **kwargs):
    if isinstance(instance.numero_operation, str):
        instance.numero_operation_pour_recherche = (
            instance.numero_operation.replace("/", "")
            .replace("-", "")
            .replace(" ", "")
            .replace(".", "")
        )


@receiver(pre_save, sender=Programme)
def compute_date_achevement_compile(sender, instance, *args, **kwargs):
    instance.date_achevement_compile = (
        instance.date_achevement or instance.date_achevement_previsible
    )
    if instance.code_postal and len(instance.code_postal) == 5:
        if instance.code_postal.isnumeric() and int(instance.code_postal) >= 97000:
            code_departement = instance.code_postal[0:3]
        else:
            code_departement = instance.code_postal[0:2]
        if (
            instance.code_insee_departement != code_departement
            and instance.code_insee_departement
            not in [
                "2A",
                "2B",
            ]
        ):
            try:
                if code_departement == "20":
                    # Cas spécial de la Corse car in n'est pas possible de déterminer le département
                    # à partir du code postal
                    departement = Departement.objects.filter(
                        code_postal=code_departement
                    ).first()
                    if departement:
                        instance.code_insee_departement = "20"
                        instance.code_insee_region = departement.code_insee_region
                else:
                    departement = Departement.objects.get(code_postal=code_departement)
                    instance.code_insee_departement = departement.code_insee
                    instance.code_insee_region = departement.code_insee_region
            except (Departement.DoesNotExist, AttributeError):
                logger.error(
                    "Le numero de departement %s n'existe pas depuis le code postal %s",
                    code_departement,
                    instance.code_postal,
                )


@receiver(post_delete, sender=Lot)
def remove_lot(sender, instance, *args, **kwargs):
    programme = Programme.objects.get(id=instance.programme_id)
    if programme.conventions.count() == 0:
        programme.delete()
