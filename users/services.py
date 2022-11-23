from typing import Optional

from django.contrib.auth.models import Group
from django.db import connection

from bailleurs.models import Bailleur
from core.services import Slugifier
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
            username: Optional[str] = None) -> User:

        if username is None:
            username = cls.generate_username(first_name, last_name)

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

    @classmethod
    def generate_username(cls, first_name: str, last_name: str) -> str:
        """
        Generate a username based on first & last names and by ensuring unicity of it.

        More precisely, if <`first_name`.`last_name`> is already used by an existing user, `.<index>` will be added at
        the end, with _index_ being the lowest available value.
        """
        username = f"{Slugifier.slugify(first_name, '')}.{Slugifier.slugify(last_name, '')}"

        with connection.cursor() as cursor:
            # Find last username matching first_name.last_name pattern in alphabetical order, if any
            cursor.execute("select username from users_user where username like %s order by username desc", [f'{username}%'])
            row = cursor.fetchone()

            if row is not None:
                # If such username exists, create the next iteration based on increased index
                existing = row[0]
                if existing == username:
                    username = f"{username}2"
                else:
                    index = int(existing[len(username):]) + 1
                    username = f"{username}{index}"

        return username
