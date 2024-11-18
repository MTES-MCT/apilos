import json
import logging
from typing import Any

from django.core.management.base import BaseCommand

from conventions.models import Convention
from programmes.models import Lot, Programme

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dryrun",
            action="store_true",
            help="Run the command in dry run mode without making any changes",
        )

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
                self._update_instance_field(
                    instance=programme, field_name=field, dryrun=options["dryrun"]
                )

        for convention in Convention.objects.all():
            for field in (
                "attached",
                "commentaires",
                "fichier_instruction_denonciation",
                "fichier_instruction_resiliation",
                "fichier_override_cerfa",
            ):
                self._update_instance_field(
                    instance=convention, field_name=field, dryrun=options["dryrun"]
                )

        for lot in Lot.objects.all():
            for field in (
                "edd_classique",
                "edd_volumetrique",
            ):
                self._update_instance_field(
                    instance=lot, field_name=field, dryrun=options["dryrun"]
                )

    def _update_instance_field(
        self, instance: Any, field_name: str, dryrun: bool = False
    ):
        field = getattr(instance, field_name)
        if not field:
            return

        self.stdout.write(
            f"Processing {instance._meta.object_name} (#{instance.pk}), on field '{field_name}'."
        )

        try:
            json_content = json.loads(field)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Failed to decode JSON content"))
            return

        if "files" not in json_content:
            self.stdout.write(
                self.style.ERROR("JSON content does not have a 'files' key")
            )
            return

        if not isinstance(json_content["files"], dict):
            self.stdout.write(
                self.style.ERROR("JSON content 'files' key is not a dict")
            )
            return

        needs_update: bool = False
        for v in json_content["files"].values():
            if "filename" in v and "realname" not in v:
                v.update({"realname": v["filename"]})
                needs_update = True

        if not needs_update:
            self.stdout.write("No update needed.")
            return

        setattr(instance, field_name, json.dumps(json_content))

        if not dryrun:
            instance.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"{"[DRYRUN] >> " if dryrun else ''}Done! Updated the instance with the new content."
            )
        )
