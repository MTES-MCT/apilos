import argparse
import logging

from django.core.management.base import BaseCommand
from django.db.models import Count

from users.models import User

logger = logging.getLogger(__name__)


def clear_siap_users_from_standalone():
    duplicates = (
        User.objects.values("email")
        .annotate(email_count=Count("email"))
        .filter(email_count__gt=1)
        .values_list("email", flat=True)
    )

    for email in list(duplicates):
        logger.info(email)

    logger.info("%s emails en doublons détectés", len(duplicates))

    users_to_delete = User.objects.filter(email__in=duplicates).exclude(
        cerbere_login=None
    )
    return users_to_delete


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

        users_to_delete = clear_siap_users_from_standalone()

        if verbose:
            for user in users_to_delete:
                logger.info(user)

        logger.info("%s utilisateurs en doublons ont été trouvé", len(users_to_delete))

        if not dry_run:
            logger.warning(
                "La commande n'a pas été lancée avec le mode dry_run, "
                "des données vont être supprimées de la base de données"
            )
            users_to_delete.delete()
