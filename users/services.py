from django.contrib.auth.models import Group

from bailleurs.models import Bailleur
from users.models import User, Role
from users.type_models import TypeRole


class UserService:
    @classmethod
    def create_user_bailleur(
            cls,
            first_name: str,
            last_name: str,
            username: str,
            email: str,
            bailleur: Bailleur) -> User:

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

        return user_bailleur
