import datetime

from django.core.management import BaseCommand
from django.conf import settings

from users.services import UserService


class Command(BaseCommand):
    help = "Envoyer les emails de récap mensuels"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Envoyer les emails quoi qu'il arrive",
        )

    def _check_envoi(self):
        # Vérification tâches CRON activées
        if not settings.CRON_ENABLED:
            self.stderr.write("Tâches CRON désactivées, abandon")
            return False

        # Vérification que le jour est valide (1er lundi du mois)
        if datetime.date.today().weekday() > 0 or datetime.date.today().day > 7:
            self.stderr.write("Pas le premier lundi du mois, abandon")
            return False

        return True

    def handle(self, *args, **options):
        force = options["force"]

        if force or self._check_envoi():

            if not settings.APPLICATION_DOMAIN_URL:
                raise Exception(
                    "La variable APPLICATION_DOMAIN_URL doit être \
définie pour pouvoir envoyer des emails"
                )

            nb_sent_emails = UserService.email_mensuel()
            self.stdout.write(
                f"{nb_sent_emails['instructeur']} email(s) \
instructeur envoyé(s)"
            )
            self.stdout.write(
                f"{nb_sent_emails['bailleur']} email(s) bailleur \
envoyé(s)"
            )
