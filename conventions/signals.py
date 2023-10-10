from typing import Any

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from conventions.models.avenant_type import AvenantType

from conventions.models import Convention, Lot
from programmes.models import Programme
from django.db.models.fields.reverse_related import ManyToOneRel


def _update_nested_convention_field(
    field_name: str,
    instance: Convention | Programme | Lot,
    previous_instance: Convention | Programme | Lot,
) -> None:
    if type(instance) != type(previous_instance):
        raise TypeError(
            f"instance and previous instance must be of the same type ({type(instance)} != {type(previous_instance)})"
        )

    if "." in field_name:
        field_as_list = field_name.split(".")  # [programme, bailleur, nom]
        instance = getattr(instance, field_as_list[0])  # <Programme>
        field_name = ".".join(field_as_list[1:])  # "bailleur.nom"
        previous_instance = getattr(previous_instance, field_as_list[0])
        _update_nested_convention_field(field_name, instance, previous_instance)
        return

    field_object = instance.__class__._meta.get_field(field_name)

    if isinstance(field_object, ManyToOneRel):
        getattr(instance, field_name).all().delete()
        for item in getattr(previous_instance, field_name).all():
            item.clone(instance)
        return

    previous_value = getattr(previous_instance, field_name)
    setattr(instance, field_name, previous_value)
    instance.save()


@receiver(m2m_changed, sender=Convention.avenant_types.through)
def post_save_reset_avenant_fields_after_block_delete(
    sender: Any,
    instance: Convention,
    action: str,
    reverse: bool,
    model: AvenantType,
    pk_set: set,
    **kwargs: Any,
):
    if (
        action == "post_remove"
        and not reverse
        and model == AvenantType
        and instance.is_avenant()
    ):
        for avenant_type in model.objects.filter(pk__in=list(pk_set)):
            last_avenant_or_parent = instance.parent

            if last_avenant_or_parent.avenants.count() > 1:
                last_avenant_or_parent = last_avenant_or_parent.avenants.all().order_by(
                    "-cree_le"
                )[1]

            for field_name in avenant_type.fields:
                _update_nested_convention_field(
                    field_name=field_name,
                    instance=instance,
                    previous_instance=last_avenant_or_parent,
                )
