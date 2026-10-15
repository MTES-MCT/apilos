import json

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from instructeurs.models import Administration
from programmes.models import Programme
from conventions.models import Convention


class Command(BaseCommand):
    help = (
        "Réaffecte l'administration des programmes par numero_convention. "
        "Mode simulation par défaut, utiliser --run pour appliquer."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--conventions",
            type=str,
            required=True,
            help="Chemin vers un fichier JSON contenant une liste de numero_convention",
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

    def _load_conventions(self, path):
        """Charge la liste des numéros de convention depuis un fichier JSON."""
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
                "Le fichier JSON doit contenir une liste de numero_convention."
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

    def _get_programmes(self, numero_conventions, new_admin, old_admin):
        """Retourne le queryset des programmes à mettre à jour."""
        programme_ids = Convention.objects.filter(
        numero__in=numero_conventions
        )   .values_list("programme_id", flat=True)

        filters = {"id__in": programme_ids}
        if old_admin:
            filters["administration"] = old_admin
        return Programme.objects.filter(**filters).exclude(
        administration=new_admin,
    )

    def _report_missing(self, numero_conventions, programme_ids):
        """Signale les conventions fournies sans programme correspondant."""
        numeros_trouves = set(
            Convention.objects.filter(
                numero__in=numero_conventions,
                programme_id__in=programme_ids,
            ).values_list("numero", flat=True)
        )
        manquants = [n for n in numero_conventions if n not in numeros_trouves]
        if manquants:
            self.stdout.write(
                self.style.WARNING(
                    f"\nConventions sans programme correspondant ({len(manquants)}) :"
                )
            )
            for numero in manquants:
                self.stdout.write(f"  - {numero}")

    def handle(self, *args, **options):
        run = options["run"]

        # Chargement de la liste des conventions
        numero_conventions = self._load_conventions(options["conventions"])
        if numero_conventions is None:
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
        self.stdout.write(f"Conventions fournies : {len(numero_conventions)}")

        # Recherche des programmes correspondants, avec les conventions
        # matchées préchargées pour l'affichage.
        programmes = list(
            self._get_programmes(numero_conventions, new_admin, old_admin).prefetch_related(
                Prefetch(
                    "conventions",
                    queryset=Convention.objects.filter(
                        numero__in=numero_conventions
                    ).only("numero", "programme_id"),
                    to_attr="matching_conventions",
                )
            )
        )

        if not programmes:
            self.stdout.write("Aucun programme trouvé pour les conventions fournies.")
            return

        self.stdout.write(f"Programmes à mettre à jour : {len(programmes)}")

        for programme in programmes:
            current_admin = programme.administration
            numeros = ", ".join(
                c.numero for c in programme.matching_conventions if c.numero
            )
            label = f"{programme.numero_operation} - {programme.nom} (conventions : {numeros})"

            if run:
                programme.administration = new_admin
                programme.save()
                self.stdout.write(f"  Mis à jour : {label}")
            else:
                self.stdout.write(
                    f"  [Simulation] {label} "
                    f"(actuel : {current_admin.code if current_admin else 'Aucune'})"
                )

        self._report_missing(numero_conventions, [p.id for p in programmes])

        if run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nTerminé. {len(programmes)} programmes mis à jour."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nSimulation terminée. Utilisez --run pour appliquer."
                )
            )