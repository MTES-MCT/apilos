from django.contrib.auth.models import Group
from django.db.models import Q

from bailleurs.models import Bailleur
from core.services import EmailService, EmailTemplateID
from users.models import User, Role
from users.type_models import TypeRole


class UserService:
    @classmethod
    def create_user_bailleur(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        bailleur: Bailleur,
        username: str,
        login_url: str,
    ) -> User:

        user_bailleur = User.objects.create_user(
            username, email, first_name=first_name, last_name=last_name
        )
        group_bailleur = Group.objects.get(
            name="bailleur",
        )
        Role.objects.create(
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=user_bailleur,
            group=group_bailleur,
        )

        password = User.objects.make_random_password()
        user_bailleur.set_password(password)
        user_bailleur.save()

        EmailService(
            to_emails=[user_bailleur.email],
            email_template_id=EmailTemplateID.B_WELCOME,
        ).send_transactional_email(
            email_data={
                "email": user_bailleur.email,
                "username": user_bailleur.username,
                "firstname": user_bailleur.first_name,
                "lastname": user_bailleur.last_name,
                "password": password,
                "login_url": login_url,
            }
        )

        return user_bailleur

    @classmethod
    def extract_username_from_email(cls, email: str | None = None):
        if email is None:
            return ""

        parts = email.split("@", maxsplit=1)

        if len(parts) > 1:
            return parts[0].lower()

        return ""

    @classmethod
    def email_mensuel(cls):
        instructeur_tous_mails = Q(
            roles__typologie="INSTRUCTEUR",
            preferences_email="TOUS",
            roles__administration__programme__conventions__statut__in=[
                "2. Instruction requise",
                "4. A signer",
            ],
        )
        instructeur_partiel_instruction = Q(
            roles__typologie="INSTRUCTEUR",
            preferences_email="PARTIEL",
            roles__administration__programme__conventions__statut="2. Instruction requise",
        )
        instructeur_partiel_signature = Q(
            roles__typologie="INSTRUCTEUR",
            preferences_email="PARTIEL",
            valide_par__convention__statut="4. A signer",
        )

        users_instructeurs = User.objects.filter(
            instructeur_tous_mails
            | instructeur_partiel_instruction
            | instructeur_partiel_signature
        ).distinct()

        bailleurs_tous_mails = Q(
            roles__typologie="BAILLEUR",
            preferences_email="TOUS",
            roles__bailleur__programme__conventions__statut__in=[
                "1. Projet",
                "3. Corrections requises",
            ],
        )
        bailleurs_partiel_projet = Q(
            roles__typologie="BAILLEUR",
            preferences_email="PARTIEL",
            convention__statut="1. Projet",
        )
        bailleurs_partiel_corrections = Q(
            roles__typologie="BAILLEUR",
            preferences_email="PARTIEL",
            valide_par__convention__statut="3. Corrections requises",
        )

        users_bailleurs = User.objects.filter(
            bailleurs_tous_mails
            | bailleurs_partiel_projet
            | bailleurs_partiel_corrections
        ).distinct()

        return users_instructeurs, users_bailleurs
