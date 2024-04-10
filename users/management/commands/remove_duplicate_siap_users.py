import argparse

from django.core.management.base import BaseCommand
from django.db.models import Count

from users.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            help="Run command without writing changes to the database",
            action=argparse.BooleanOptionalAction,
            default=False,
        )

        parser.add_argument(
            "--verbose",
            help="print all users to delete",
            action=argparse.BooleanOptionalAction,
            default=False,
        )

    def handle(self, *args, **options):
        verbose = options.get("verbose")
        dry_run = options.get("dry_run")

        users_to_delete = self._find_standalone_users_with_siap_account()

        if verbose:
            for user in users_to_delete:
                self.stdout.write(user)

        self.stdout.write(
            "%s utilisateurs en doublons ont été trouvé", len(users_to_delete)
        )

        if not dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "La commande n'a pas été lancée avec le mode dry_run, "
                    "des données vont être supprimées de la base de données"
                )
            )
            users_to_delete.delete()

    def _find_standalone_users_with_siap_account(self):
        duplicates = (
            User.objects.values("email")
            .annotate(email_count=Count("email"))
            .filter(email_count__gt=1)
            .exclude(is_superuser=True)
            .exclude(is_staff=True)
            .values_list("email", flat=True)
        )

        for email in list(duplicates):
            self.stdout.write(email)

        users_to_delete = (
            User.objects.filter(email__in=duplicates, cerbere_login=None)
            .exclude(is_superuser=True)
            .exclude(is_staff=True)
        )

        return users_to_delete
