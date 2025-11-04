import csv
import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from bailleurs.models import Bailleur
from conventions.models import Convention
from programmes.models.models import Programme


class Command(BaseCommand):
    help = (
        "Met à jour les bailleurs pour les Programmes. "
        "Peut transférer tous les Programmes d'un Bailleur à un autre, "
        "ou mettre à jour en se basant sur un fichier JSON de conventions."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--old-bailleur",
            type=str,
            help="SIREN (9 chiffres) ou SIRET (14 chiffres) de l'ancien Bailleur",
        )
        parser.add_argument(
            "--new-bailleur",
            type=str,
            help="SIREN (9 chiffres) ou SIRET (14 chiffres) du nouveau Bailleur",
        )
        parser.add_argument(
            "--run",
            action="store_true",
            help="Effectuer réellement le transfert ; sans ce flag, le script ne fera qu'une simulation",
        )
        parser.add_argument(
            "--file",
            type=str,
            help="Chemin vers le fichier JSON contenant les mises à jour de conventions",
        )

    def get_bailleur(self, identifier: str) -> Bailleur:
        if len(identifier) == 14:
            return Bailleur.objects.get(siret=identifier)
        elif len(identifier) == 9:
            return Bailleur.objects.get(siren=identifier)
        else:
            raise CommandError(
                f"L'identifiant {identifier} n'est pas un SIREN (9) ou SIRET (14) valide"
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
        for check_numero in [numero, numero.replace(" ", "-")]:
            try:
                return Convention.objects.get(numero=check_numero)
            except ObjectDoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Convention introuvable: {numero}")
                )

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

    def _process_convention(self, convention, writer_updates, writer_name_diff, run):
        numero = convention["id"]
        expected_name = convention["bailleur"]
        siren_siret = convention["siren_siret"].replace(" ", "")

        conv = self._get_convention(numero)
        if not conv:
            return False

        bailleur = self._get_bailleur(siren_siret, numero)
        if not bailleur:
            return False

        old_bailleur = conv.programme.bailleur

        # log before update
        self.log_update(writer_updates, numero, old_bailleur, bailleur)

        if run:
            # update convention
            conv.programme.bailleur = bailleur
            conv.programme.save()

        # check mismatch
        if expected_name.strip().lower() not in bailleur.nom.strip().lower():
            self.log_name_diff(writer_name_diff, numero, expected_name, bailleur)

        return True

    def handle(self, *args, **options):
        run = options.get("run", False)

        # Case 1: Transfer all programmes between two bailleurs
        if options.get("old_bailleur") and options.get("new_bailleur"):
            old_bailleur = self.get_bailleur(options["old_bailleur"])
            new_bailleur = self.get_bailleur(options["new_bailleur"])

            programmes_to_update = Programme.objects.filter(bailleur=old_bailleur)
            count_old = programmes_to_update.count()

            if count_old == 0:
                self.stdout.write(
                    self.style.WARNING(f"Aucun Programme trouvé pour {old_bailleur}")
                )
                return

            if run:
                updated = programmes_to_update.update(bailleur=new_bailleur)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{updated} Programmes transférés de {old_bailleur} vers {new_bailleur}"
                    )
                )
            else:
                for prog in programmes_to_update:
                    self.stdout.write(f"- {prog}")

                self.stdout.write(
                    self.style.NOTICE(
                        f"[Simulation] {count_old} Programmes seraient transférés de {old_bailleur} vers {new_bailleur}"
                    )
                )
        # Case 2: Update from a JSON file
        elif options.get("file"):
            conventions = self._read_json(json_file=options["file"])
            if not conventions:
                self.stdout.write(self.style.ERROR("Aucune convention à traiter."))
                return

            updated_count = 0
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

                # process all conventions
                for convention in conventions:
                    if self._process_convention(
                        convention, writer_updates, writer_name_diff, run
                    ):
                        updated_count += 1

            if run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Mise à jour JSON terminée. "
                        f"{updated_count} conventions mises à jour avec succès, "
                        f"{len(conventions) - updated_count} non mises à jour. "
                        "Consultez les fichiers générés pour aperçu : "
                        "updated_conventions.csv et name_diff_conventions.csv"
                    )
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(
                        f"[Simulation] Mise à jour JSON terminé. "
                        f"{updated_count} conventions mises à jour avec succès, "
                        f"{len(conventions) - updated_count} non mises à jour. "
                        "Aucune mise à jour appliquée. "
                        "Consultez les fichiers générés pour aperçu : "
                        "updated_conventions.csv et name_diff_conventions.csv"
                    )
                )

        else:
            self.stdout.write(
                self.style.ERROR(
                    "Vous devez fournir soit --old-bailleur et --new-bailleur, soit --file"
                )
            )
