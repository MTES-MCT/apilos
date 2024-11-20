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
        parser.add_argument(
            "--year",
            type=int,
            required=True,
        )

    def handle(self, *args, **options):
        year = options["year"]
        self.stdout.write(f" >> Fixing text and files fields for year {year}")

        queryset = Programme.objects.filter(cree_le__year=year)
        self.stdout.write(f" >> Processing {queryset.count()} programmes")
        for programme in queryset:
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

        queryset = Convention.objects.filter(cree_le__year=year)
        self.stdout.write(f" >> Processing {queryset.count()} conventions")
        for convention in queryset:
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

        queryset = Lot.objects.filter(cree_le__year=year)
        self.stdout.write(f" >> Processing {queryset.count()} lots")
        for lot in queryset:
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

        try:
            json_content = json.loads(field)
        except json.JSONDecodeError:
            return

        if "files" not in json_content:
            return

        if not isinstance(json_content["files"], dict):
            return

        needs_update: bool = False
        for v in json_content["files"].values():
            if "filename" in v and "realname" not in v:
                v.update({"realname": v["filename"]})
                needs_update = True

        if not needs_update:
            return

        setattr(instance, field_name, json.dumps(json_content))

        self.stdout.write(
            f"{'[DRYRUN] >> ' if dryrun else ''}Processing {instance._meta.object_name} (#{instance.pk}), on field '{field_name}'."  # noqa: E501
        )
        if not dryrun:
            instance.save()
