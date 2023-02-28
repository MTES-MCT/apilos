from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.core.validators import validate_email

from django.db import transaction

from core.services import EmailService, EmailTemplateID
from instructeurs.models import Administration
from users.models import User, Role
from users.type_models import TypeRole


class Command(BaseCommand):
    help = "Crée et initialise un utilisateur instructeur"

    def add_arguments(self, parser):
        parser.add_argument(
            "nom",
            type=str,
            help="Nom de famille",
        )

        parser.add_argument(
            "prenom",
            type=str,
            help="Prénom",
        )

        parser.add_argument(
            "email",
            type=str,
            help="Courriel",
        )

        parser.add_argument(
            "administrations",
            nargs="+",
            type=str,
            default=[],
            help="Code des administrations à affecter à l'instructeur",
        )

    def handle(self, *args, **options):
        prenom = options["prenom"]
        nom = options["nom"]
        email = options["email"]
        administrations = [
            Administration.objects.filter(code=code).first()
            for code in options["administrations"]
        ]

        if len(administrations) == 0:
            print("Aucune administration trouvée, création d'instructeur annulée")
        else:
            validate_email(email)
            if User.objects.filter(email=email).first() is not None:
                print("Instructeur already exists, skipped")
            else:
                with transaction.atomic():
                    user = User.objects.create(
                        email=email,
                        username=email,
                        first_name=prenom,
                        last_name=nom,
                    )

                    password = User.objects.make_random_password()
                    user.set_password(password)
                    user.save()

                    for administration in administrations:
                        Role.objects.create(
                            typologie=TypeRole.INSTRUCTEUR,
                            administration=administration,
                            user=user,
                            group=Group.objects.get(name="instructeur"),
                        )

                    EmailService(
                        to_emails=[user.email],
                        email_template_id=EmailTemplateID.I_WELCOME,
                    ).send_transactional_email(
                        email_data={
                            "email": user.email,
                            "username": user.username,
                            "firstname": user.first_name,
                            "lastname": user.last_name,
                            "password": password,
                            "login_url": "https://apilos.beta.gouv.fr/accounts/login/?instructeur=1",
                        }
                    )
