import string
import random

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Group

from faker import Faker

from instructeurs.models import Administration
from bailleurs.models import Bailleur, TypeBailleur
from conventions.models import Convention
from programmes.models import (
    Programme,
    Financement,
    Lot,
    TypeOperation,
    Zone123,
    ZoneABC,
)
from users.models import User, Role
from users.type_models import TypeRole


bailleur = {
    "nom": "Bailleur HLM de test",
    "pk": 1,
    "siret": "12345678900000",
    "type_bailleur": TypeBailleur.OFFICE_PUBLIC_HLM,
    "capital_social": 10000.01,
    "adresse": "1 place de la république",
    "code_postal": "00100",
    "ville": "Ma Ville",
    "signataire_nom": "John Doe",
    "signataire_fonction": "Directeur",
    "signataire_date_deliberation": "2020-01-01",
}

administration = {
    "nom": "Administration DAP Test",
    "pk": 1,
    "code": "00000",
    "ville_signature": "Ma ville sur Fleuve",
}


def generate_programmes(num):
    fake = Faker("fr_FR")
    programmes = []
    random_name = [
        fake.name(),
        fake.color_name(),
        fake.region(),
        fake.department_name(),
        fake.first_name(),
    ]
    for _ in range(num):
        fin = random.choice([Financement.PLAI, Financement.PLS, Financement.PLUS]).value
        lots = [{"nb_logements": random.randint(1, 30), "financement": fin}]
        fin2 = random.choice(
            [Financement.PLAI, Financement.PLS, Financement.PLUS]
        ).value
        if fin2 != fin:
            lots.append({"nb_logements": random.randint(1, 30), "financement": fin2})
        programmes.append(
            {
                "nom": random.choice(
                    [
                        "Résidence ",
                        "Les jardins de ",
                        "Les terrasses de ",
                        "Le clos ",
                    ]
                )
                + f"{''.join(random.choice(random_name))}",
                "code_postal": f"001{random.randint(0,9)}{random.randint(0,9)}",
                "ville": f"Ma Ville {random.choice(string.ascii_uppercase)}",
                "adresse": None,
                "numero_galion": f"{random.randint(0,9)}{random.randint(0,9)}"
                + f"{random.randint(0,9)}{random.randint(0,9)}00000"
                + f"{random.randint(0,9)}{random.randint(0,9)}"
                + f"{random.randint(0,9)}{random.randint(0,9)}",
                "annee_gestion_programmation": 2022,
                "zone_123": random.choice(
                    [Zone123.Zone1, Zone123.Zone2, Zone123.Zone3]
                ).value,
                "zone_abc": random.choice(
                    [
                        ZoneABC.ZoneA,
                        ZoneABC.ZoneB1,
                        ZoneABC.ZoneB2,
                        ZoneABC.ZoneC,
                    ]
                ).value,
                "type_operation": random.choice(TypeOperation.choices)[0],
                "lots": lots,
            }
        )
    return programmes


class Command(BaseCommand):
    # pylint: disable=R0912,R0914,R0915
    def handle(self, *args, **options):

        administration_test, _ = Administration.objects.get_or_create(
            code=administration["code"], defaults=administration
        )

        bailleur_test, _ = Bailleur.objects.get_or_create(
            siret=bailleur["siret"], defaults=bailleur
        )

        if settings.ENVIRONMENT == "production":
            raise Exception("il est interdit d'executer cette command en production")

            # Remove conventions and operation and lot
        truncate_programme = False
        inp = input("Do you want to truncate Conventions/Operations/Lots (N/y) ?")
        if inp.lower() in ["y", "yes", "oui"]:
            truncate_programme = True
        elif inp.lower() in ["n", "no", "non"]:
            truncate_programme = False
        else:
            print("Using default option: Operation won't be truncated")
        if truncate_programme:
            Programme.objects.all().delete()
            Convention.objects.all().delete()

        # Remove user
        truncate_users = False
        inp = input("Do you want to truncate Users (N/y) ?")
        if inp.lower() in ["y", "yes", "oui"]:
            truncate_users = True
        elif inp.lower() in ["n", "no", "non"]:
            truncate_users = False
        else:
            print("Using default option: Users won't be truncated")
        if truncate_users:
            User.objects.exclude(email__contains="beta.gouv.fr").delete()

        if not User.objects.filter(username="demo.bailleur").exists():
            user_bailleur = User.objects.create_user(
                "demo.bailleur", "demo.bailleur@oudard.org", "demo.12345"
            )
            user_bailleur.first_name = "DEMO"
            user_bailleur.last_name = "Bailleur"
            user_bailleur.save()
            group_bailleur = Group.objects.get(
                name="bailleur",
            )
            Role.objects.create(
                typologie=TypeRole.BAILLEUR,
                bailleur=bailleur_test,
                user=user_bailleur,
                group=group_bailleur,
            )

        if not User.objects.filter(username="demo.instructeur").exists():
            user_instructeur = User.objects.create_user(
                "demo.instructeur", "demo.instructeur@oudard.org", "instru12345"
            )
            user_instructeur.first_name = "DEMO"
            user_instructeur.last_name = "Instructeur"
            user_instructeur.save()
            group_instructeur = Group.objects.get(
                name="instructeur",
            )
            Role.objects.create(
                typologie=TypeRole.INSTRUCTEUR,
                administration=administration_test,
                user=user_instructeur,
                group=group_instructeur,
            )

        for programme in generate_programmes(30):
            lots = programme.pop("lots")
            programme_test, _ = Programme.objects.get_or_create(
                **programme, administration=administration_test, bailleur=bailleur_test
            )
            for lot in lots:
                Lot.objects.get_or_create(**lot, programme=programme_test)
