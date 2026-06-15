"""
Commande de diagnostic : liste les utilisateurs bailleur et instructeur
liés à une administration donnée (par son code), et optionnellement les
détails d'une opération spécifique.

Utile pour investiguer les problèmes de notification par email :
- Vérifie quels utilisateurs ont un rôle local dans APiLos
- Affiche leur préférence email (TOUS, PARTIEL, AUCUN)
- Affiche leur dernière connexion
- Affiche les destinataires email pour une convention donnée

Utilisation :
    python manage.py list_users_by_administration <code_administration>
    python manage.py list_users_by_administration <code_administration> --operation <numero_operation>

Exemples :
    python manage.py list_users_by_administration 33063
    python manage.py list_users_by_administration 33063 --operation 2021330630053
"""

from django.core.management.base import BaseCommand, CommandError

from bailleurs.models import Bailleur
from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Programme
from users.models import User
from users.type_models import TypeRole


class Command(BaseCommand):
    help = (
        "Liste les utilisateurs bailleur et instructeur liés à une administration "
        "(par code). Utile pour diagnostiquer les problèmes de notification email."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "code",
            type=str,
            help="Code de l'administration (ex: 33063 pour Bordeaux Métropole)",
        )
        parser.add_argument(
            "--operation",
            type=str,
            default=None,
            help="Numéro d'opération pour afficher le détail d'une convention spécifique",
        )

    def handle(self, *args, **options):
        code = options["code"]
        operation = options["operation"]

        try:
            admin = Administration.objects.get(code=code)
        except Administration.DoesNotExist as err:
            raise CommandError(
                f"Administration avec le code '{code}' introuvable."
            ) from err

        self.stdout.write(self.style.SUCCESS(f"Administration: {admin}"))

        # Conventions count
        conventions = Convention.objects.filter(programme__administration=admin)
        self.stdout.write(f"Nb conventions: {conventions.count()}")

        # Bailleurs linked via Programme
        bailleur_ids = conventions.values_list(
            "programme__bailleur", flat=True
        ).distinct()
        bailleurs = Bailleur.objects.filter(id__in=bailleur_ids)
        self.stdout.write(self.style.SUCCESS(f"\nBailleurs ({bailleurs.count()}):"))
        for b in bailleurs:
            self.stdout.write(f"  - {b.nom} (SIREN: {b.siren})")

        # Bailleur users (via Role)
        users_bailleur = (
            User.objects.filter(
                roles__typologie=TypeRole.BAILLEUR,
                roles__bailleur__in=bailleurs,
            )
            .distinct()
            .order_by("email")
        )
        self.stdout.write(
            self.style.SUCCESS(f"\nUtilisateurs bailleur ({users_bailleur.count()}):")
        )
        for u in users_bailleur:
            self.stdout.write(
                f"  {u.email} | pref_email={u.preferences_email} | last_login={u.last_login}"
            )

        # Instructeur users
        users_instructeur = (
            User.objects.filter(
                roles__typologie=TypeRole.INSTRUCTEUR,
                roles__administration=admin,
            )
            .distinct()
            .order_by("email")
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"\nUtilisateurs instructeur ({users_instructeur.count()}):"
            )
        )
        for u in users_instructeur:
            self.stdout.write(
                f"  {u.email} | pref_email={u.preferences_email} | last_login={u.last_login}"
            )

        # Détail d'une opération spécifique
        if operation:
            self._display_operation_details(operation)

    def _display_operation_details(self, numero_operation: str):
        self.stdout.write(
            self.style.SUCCESS(f"\n--- Détail opération {numero_operation} ---")
        )

        programmes = Programme.objects.filter(numero_operation=numero_operation)
        if not programmes.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Aucun programme trouvé pour l'opération {numero_operation}"
                )
            )
            return

        for programme in programmes:
            self.stdout.write(
                f"\nProgramme: {programme.nom} | Bailleur: {programme.bailleur.nom} "
                f"(SIREN: {programme.bailleur.siren})"
            )

            for conv in programme.conventions.all():
                self._display_convention_details(conv)

    def _display_convention_details(self, conv):
        self.stdout.write(f"\n  Convention: {conv.uuid} | statut={conv.statut}")
        self.stdout.write(
            f"    Emails bailleur destinataires: {conv.get_email_bailleur_users()}"
        )
        self.stdout.write(
            f"    Emails instructeur destinataires: {conv.get_email_instructeur_users()}"
        )

        # Historique des interactions
        histories = conv.conventionhistories.select_related("user").order_by(
            "-cree_le"
        )[:10]
        if histories:
            self.stdout.write("    Dernières interactions:")
            for h in histories:
                email = h.user.email if h.user else "N/A"
                self.stdout.write(
                    f"      {email} | statut={h.statut_convention} | {h.cree_le}"
                )
