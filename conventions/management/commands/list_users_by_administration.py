"""
Commande de diagnostic : liste les utilisateurs bailleur et instructeur
liés à une administration donnée (par son code).

Utile pour investiguer les problèmes de notification par email :
- Vérifie quels utilisateurs ont un rôle local dans APiLos
- Affiche leur préférence email (TOUS, PARTIEL, AUCUN)
- Affiche leur dernière connexion

Utilisation :
    python manage.py list_users_by_administration <code_administration>

Exemple :
    python manage.py list_users_by_administration 33063
"""

from django.core.management.base import BaseCommand, CommandError

from bailleurs.models import Bailleur
from conventions.models import Convention
from instructeurs.models import Administration
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

    def handle(self, *args, **options):
        code = options["code"]

        try:
            admin = Administration.objects.get(code=code)
        except Administration.DoesNotExist as err:
            raise CommandError(f"Administration with code '{code}' not found.") from err

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
