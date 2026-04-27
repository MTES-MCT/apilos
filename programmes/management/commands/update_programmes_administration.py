import json

from django.core.management.base import BaseCommand

from instructeurs.models import Administration
from programmes.models import Programme


class Command(BaseCommand):
    help = (
        "Réaffecte l'administration des programmes par numero_operation. "
        "Mode simulation par défaut, utiliser --run pour appliquer."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--operations",
            type=str,
            required=True,
            help="Chemin vers un fichier JSON contenant une liste de numero_operation",
        )
        parser.add_argument(
            "--new_administration",
            type=str,
            required=True,
            help="Code de l'administration cible (ex : 31555)",
        )
        parser.add_argument(
            "--old_administration",
            type=str,
            required=False,
            default=None,
            help="Code de l'administration actuelle (ex : DDI031). "
            "Filtre optionnel ; si omis, met à jour tous les programmes correspondants "
            "qui ne sont pas déjà rattachés à la nouvelle administration.",
        )
        parser.add_argument(
            "--run",
            action="store_true",
            help="Appliquer les modifications en base. Par défaut : simulation.",
        )

    def _load_operations(self, path):
        """Charge la liste des numéros d'opération depuis un fichier JSON."""
        try:
            with open(path) as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(f"Fichier '{path}' introuvable.")
            return None
        except json.JSONDecodeError:
            self.stderr.write(f"Le fichier '{path}' n'est pas un JSON valide.")
            return None

        if not isinstance(data, list):
            self.stderr.write(
                "Le fichier JSON doit contenir une liste de numero_operation."
            )
            return None
        return data

    def _get_administration(self, code):
        """Récupère une administration par son code, ou None si introuvable."""
        try:
            return Administration.objects.get(code=code)
        except Administration.DoesNotExist:
            self.stderr.write(f"L'administration avec le code '{code}' n'existe pas.")
            return None

    def _get_programmes(self, numero_operations, new_admin, old_admin):
        """Retourne le queryset des programmes à mettre à jour."""
        filters = {"numero_operation__in": numero_operations}
        if old_admin:
            filters["administration"] = old_admin
        return Programme.objects.filter(**filters).exclude(
            administration=new_admin,
        )

    def _report_missing(self, numero_operations, programmes):
        """Signale les opérations non trouvées."""
        found_operations = set(programmes.values_list("numero_operation", flat=True))
        missing = set(numero_operations) - found_operations
        if missing:
            self.stderr.write(f"\n{len(missing)} opération(s) non trouvée(s) :")
            for op in sorted(missing):
                self.stderr.write(f"  - {op}")

    def handle(self, *args, **options):
        run = options["run"]

        # Chargement de la liste des opérations
        numero_operations = self._load_operations(options["operations"])
        if numero_operations is None:
            return

        # Validation des administrations
        new_admin = self._get_administration(options["new_administration"])
        if new_admin is None:
            return

        old_admin = None
        if options["old_administration"]:
            old_admin = self._get_administration(options["old_administration"])
            if old_admin is None:
                return

        if old_admin:
            self.stdout.write(
                f"Réaffectation des programmes de '{old_admin}' vers '{new_admin}'"
            )
        else:
            self.stdout.write(f"Réaffectation des programmes vers '{new_admin}'")
        self.stdout.write(f"Opérations fournies : {len(numero_operations)}")

        # Recherche des programmes correspondants
        programmes = self._get_programmes(numero_operations, new_admin, old_admin)

        if not programmes.exists():
            self.stdout.write("Aucun programme trouvé pour les opérations fournies.")
            return

        self.stdout.write(f"Programmes à mettre à jour : {programmes.count()}")

        for programme in programmes:
            current_admin = programme.administration
            if run:
                programme.administration = new_admin
                programme.save()
                self.stdout.write(
                    f"  Mis à jour : {programme.numero_operation} - {programme.nom}"
                )
            else:
                self.stdout.write(
                    f"  [Simulation] {programme.numero_operation} - {programme.nom} "
                    f"(actuel : {current_admin.code if current_admin else 'Aucune'})"
                )

        self._report_missing(numero_operations, programmes)

        if run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nTerminé. {programmes.count()} programmes mis à jour."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nSimulation terminée. Utilisez --run pour appliquer."
                )
            )
