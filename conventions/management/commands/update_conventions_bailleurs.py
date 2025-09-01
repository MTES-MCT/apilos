import csv
import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from bailleurs.models import Bailleur
from conventions.models import Convention


class Command(BaseCommand):
    help = "Update bailleurs for conventions from a JSON file and log changes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to JSON file containing convention updates",
            required=True,
        )

    def _read_json(self, json_file):
        try:
            with open(json_file, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Fichier JSON introuvable: {json_file}")
            )
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Erreur lecture JSON: {e}"))
        return []

    def _get_convention(self, numero):
        try:
            return Convention.objects.get(numero=numero)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.WARNING(f"Convention introuvable: {numero}"))
            return None

    def _get_bailleur(self, siren_siret, numero):
        try:
            return Bailleur.objects.get(siren=siren_siret)
        except ObjectDoesNotExist:
            try:
                return Bailleur.objects.get(siret=siren_siret)
            except ObjectDoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Bailleur introuvable (SIREN={siren_siret}) pour {numero}"
                    )
                )
                return None

    def log_update(self, writer, numero, old_bailleur, new_bailleur):
        writer.writerow(
            [
                numero,
                old_bailleur.nom if old_bailleur else None,
                old_bailleur.siren if old_bailleur else None,
                new_bailleur.nom,
                new_bailleur.siren,
            ]
        )

    def log_name_diff(self, writer, numero, expected_name, bailleur):
        writer.writerow([numero, expected_name, bailleur.nom, bailleur.siren])
        self.stdout.write(
            self.style.WARNING(
                f"[WARN] Nom différent pour {numero}: "
                f"attendu='{expected_name}' trouvé='{bailleur.nom}'"
            )
        )

    def _process_convention(self, convention, writer_updates, writer_name_diff):
        numero = convention["id"]
        expected_name = convention["bailleur"]
        siren_siret = convention["siren_siret"].replace(" ", "")

        conv = self._get_convention(numero)
        if not conv:
            return

        bailleur = self._get_bailleur(siren_siret, numero)
        if not bailleur:
            return

        old_bailleur = conv.programme.bailleur

        # log before update
        self.log_update(writer_updates, numero, old_bailleur, bailleur)

        # update convention
        conv.programme.bailleur = bailleur
        conv.programme.save()

        # check mismatch
        if expected_name.strip().lower() not in bailleur.nom.strip().lower():
            self.log_name_diff(writer_name_diff, numero, expected_name, bailleur)

    def handle(self, *args, **options):
        conventions = self._read_json(json_file=options["file"])
        if not conventions:
            # If the JSON is empty or invalid, exit early
            self.stdout.write(self.style.ERROR("Aucune convention à traiter."))
            return

        with open(
            "updated_conventions.csv", "w", newline="", encoding="utf-8"
        ) as log_updates, open(
            "name_diff_conventions.csv", "w", newline="", encoding="utf-8"
        ) as log_name_diff:

            writer_updates = csv.writer(log_updates)
            writer_name_diff = csv.writer(log_name_diff)

            # headers
            writer_updates.writerow(
                [
                    "numero_convention",
                    "old_bailleur_name",
                    "old_bailleur_siren",
                    "new_bailleur_name",
                    "new_bailleur_siren",
                ]
            )
            writer_name_diff.writerow(
                [
                    "numero_convention",
                    "expected_bailleur_name",
                    "db_bailleur_name",
                    "siren",
                ]
            )

            # process all
            for convention in conventions:
                self._process_convention(convention, writer_updates, writer_name_diff)

        self.stdout.write(
            self.style.SUCCESS(
                "Script terminé. Fichiers générés : updated_conventions.csv "
                "et name_diff_conventions.csv"
            )
        )
