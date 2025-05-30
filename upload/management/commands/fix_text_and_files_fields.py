import argparse
import json
import logging
from datetime import date, datetime
from typing import Any

from django.core.management.base import BaseCommand

from conventions.models import Convention
from programmes.models import Lot, Programme

logger = logging.getLogger(__name__)


def validate_date_param(str_date: str) -> date:
    try:
        return datetime.strptime(str_date, "%Y-%m-%d").date()
    except ValueError as err:
        raise argparse.ArgumentTypeError(f"not a valid date: {str_date!r}") from err


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dryrun",
            action="store_true",
            help="Run the command in dry run mode without making any changes",
        )
        parser.add_argument(
            "--from-date",
            help="The start date (format YYYY-MM-DD)",
            required=True,
            type=validate_date_param,
        )
        parser.add_argument(
            "--to-date",
            help="The end date (format YYYY-MM-DD)",
            required=True,
            type=validate_date_param,
        )
        parser.add_argument(
            "--fix-realname",
            action="store_true",
            help="Fix the realname field in the text and files fields",
        )
        parser.add_argument(
            "--fix-special-characters",
            action="store_true",
            help="Fix special characters in the text and files fields",
        )

    def handle(self, *args, **options):
        from_date = options["from_date"]
        to_date = options["to_date"]
        if from_date > to_date:
            raise ValueError("The start date must be before the end date")

        self.stdout.write(
            f" >> Fixing text and files fields for {from_date} to {to_date}"
        )

        queryset = Programme.objects.filter(
            cree_le__date__gte=from_date, cree_le__date__lt=to_date
        )
        self.stdout.write(f" >> Processing {queryset.count()} programmes")
        for programme in queryset:
            for field_name in (
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
                self._do_work(instance=programme, field_name=field_name, **options)

        queryset = Convention.objects.filter(
            cree_le__date__gte=from_date, cree_le__date__lt=to_date
        )
        self.stdout.write(f" >> Processing {queryset.count()} conventions")
        for convention in queryset:
            for field_name in (
                "attached",
                "commentaires",
                "fichier_instruction_denonciation",
                "fichier_instruction_resiliation",
                "fichier_override_cerfa",
            ):
                self._do_work(instance=convention, field_name=field_name, **options)

        queryset = Lot.objects.filter(
            cree_le__date__gte=from_date, cree_le__date__lt=to_date
        )
        self.stdout.write(f" >> Processing {queryset.count()} lots")
        for lot in queryset:
            for field_name in (
                "edd_classique",
                "edd_volumetrique",
            ):
                self._do_work(instance=lot, field_name=field_name, **options)

    def _do_work(self, instance: Any, field_name: str, **options):
        if options["fix_realname"]:
            self._update_realname_field(
                instance=instance, field_name=field_name, dryrun=options["dryrun"]
            )
        if options["fix_special_characters"]:
            self._fix_special_characters(
                instance=instance, field_name=field_name, dryrun=options["dryrun"]
            )

    def _update_realname_field(
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
            f"{'[DRYRUN] >> ' if dryrun else ''}Processing {instance._meta.object_name} (#{instance.pk}), on field '{field_name}': updating files realname."  # noqa: E501
        )
        if not dryrun:
            instance.save()

    def _fix_special_characters(
        self, instance: Any, field_name: str, dryrun: bool = False
    ):
        content = getattr(instance, field_name)
        if not content:
            return

        try:
            json.loads(content)
        except json.JSONDecodeError:
            pass
        else:
            return

        content = (
            content.encode("utf-8")
            .replace(b"\r", b"")
            .replace(b"\n", b"")
            .replace(b"\t", b"")
            .decode("utf-8")
        )
        try:
            json_content = json.loads(content)
        except json.JSONDecodeError:
            self.stdout.write(
                "Unable to fix special characters for {instance._meta.object_name} (#{instance.pk}), on field '{field_name}."  # noqa: E501
            )

        setattr(instance, field_name, json.dumps(json_content))

        self.stdout.write(
            f"{'[DRYRUN] >> ' if dryrun else ''}Processing {instance._meta.object_name} (#{instance.pk}), on field '{field_name}': fix special characters."  # noqa: E501
        )
        if not dryrun:
            instance.save()
