from django.core.management import BaseCommand

from users.tasks import send_monthly_emails


class Command(BaseCommand):
    help = "Envoyer les emails de récap mensuels"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Envoyer les emails quoi qu'il arrive",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            "Création d'une tâche pour envoyer les emails de récap mensuels."
        )
        response = send_monthly_emails.delay(no_verify=options["force"])

        self.stdout.write("En attente de la réponse ...")
        result = response.get()

        if result is None:
            self.stdout.write(self.style.WARNING("Aucun email envoyé"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"{result['instructeur']} email(s) instructeur envoyé(s)"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"{result['bailleur']} email(s) bailleur envoyé(s)")
        )
