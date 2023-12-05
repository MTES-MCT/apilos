from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        staff_user_perms = []
        for model_name in (
            "administration",
            "annexe",
            "avenanttype",
            "bailleur",
            "convention",
            "departement",
            "ecoloreference",
            "evenement",
            "indiceevolutionloyer",
            "locauxcollectifs",
            "logement",
            "logementedd",
            "lot",
            "pret",
            "programme",
            "referencecadastrale",
            "repartitionsurface",
            "typestationnement",
            "user",
        ):
            staff_user_perms.extend(
                [f"view_{model_name}", f"add_{model_name}", f"change_{model_name}"]
            )

        permissions = Permission.objects.filter(codename__in=staff_user_perms)
        for user in User.objects.filter(is_staff=True, is_superuser=False):
            user.user_permissions.clear()
            user.user_permissions.add(*permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Added staff user permissions to '{user} ({user.email})'"
                )
            )
