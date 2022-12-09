from django.contrib.auth.models import Group

from bailleurs.models import Bailleur
from core.services import EmailService
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
            login_url: str
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

        EmailService().send_welcome_email(
            user_bailleur,
            password,
            login_url
        )

        return user_bailleur

    @classmethod
    def extract_username_from_email(cls, email: str | None = None):
        if email is None:
            return ''

        parts = email.split('@', maxsplit=1)

        if len(parts) > 1:
            return parts[0].lower()

        return ''
