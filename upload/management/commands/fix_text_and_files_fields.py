import json
import logging
from typing import Any

from django.core.management.base import BaseCommand

from conventions.models import Convention
from programmes.models import Lot, Programme

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for programme in Programme.objects.all():
            for field in (
                "acquereur",
                "acte_de_propriete",
                "certificat_adressage",
                "edd_stationnements",
                "effet_relatif",
                "reference_cadastrale",
                "reference_notaire",
                "reference_publication_acte",
                "vendeur",
            ):
                self._update_instance_field(instance=programme, field_name=field)

        for convention in Convention.objects.all():
            for field in (
                "attached",
                "commentaires",
                "fichier_instruction_denonciation",
                "fichier_instruction_resiliation",
                "fichier_override_cerfa",
            ):
                self._update_instance_field(instance=convention, field_name=field)

        for lot in Lot.objects.all():
            for field in (
                "edd_classique",
                "edd_volumetrique",
            ):
                self._update_instance_field(instance=lot, field_name=field)

    def _update_instance_field(self, instance: Any, field_name: str):
        field = getattr(instance, field_name)
        if not field:
            return

        self.stdout.write(
            self.style.SUCCESS(f"Processing {instance} field {field_name}")
        )

        try:
            json_content = json.loads(field)
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to decode JSON content for {instance} field {field_name}"
                )
            )
            return

        if "files" not in json_content:
            self.stdout.write(
                self.style.ERROR(
                    f"JSON content for {instance} field {field_name} does not contain 'files' key"
                )
            )
            return
        if not isinstance(json_content["files"], dict):
            self.stdout.write(
                self.style.ERROR(
                    f"JSON content for {instance} field {field_name} 'files' key is not a dict"
                )
            )
            return

        for v in json_content["files"].values():
            v.update({"realname": v["filename"]})

        setattr(instance, field_name, json.dumps(json_content))
        instance.save()
