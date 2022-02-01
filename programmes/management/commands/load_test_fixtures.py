import string
import random

from django.core.management.base import BaseCommand
from instructeurs.models import Administration
from bailleurs.models import Bailleur, TypeBailleur
from programmes.models import (
    Programme,
    Financement,
    Lot,
    TypeHabitat,
    TypeOperation,
    Zone123bis,
    ZoneABCbis,
)


bailleur = {
    "nom": "Bailleur HLM de test",
    "siret": "12345678900000",
    "type_bailleur": TypeBailleur.OFFICE_PUBLIC_HLM,
    "capital_social": 10000.01,
    "adresse": "1 place de la répubique",
    "code_postal": "00100",
    "ville": "Ma Ville",
    "signataire_nom": "John Doe",
    "signataire_fonction": "Directeur",
    "signataire_date_deliberation": "2020-01-01",
}

administration = {
    "nom": "Administration DAP Test",
    "code": "00000",
    "ville_signature": "Ma ville sur Fleuve",
}


def generate_programmes(num):
    programmes = []
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
                "nom": "Opération "
                + f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}",
                "code_postal": f"001{random.randint(0,9)}{random.randint(0,9)}",
                "ville": f"Ma Ville {random.choice(string.ascii_uppercase)}",
                "adresse": None,
                "numero_galion": f"{random.randint(0,9)}{random.randint(0,9)}"
                + f"{random.randint(0,9)}{random.randint(0,9)}00000"
                + f"{random.randint(0,9)}{random.randint(0,9)}"
                + f"{random.randint(0,9)}{random.randint(0,9)}",
                "annee_gestion_programmation": 2022,
                "zone_123_bis": random.choice(
                    [Zone123bis.Zone1, Zone123bis.Zone2, Zone123bis.Zone3]
                ).value,
                "zone_abc_bis": random.choice(
                    [
                        ZoneABCbis.ZoneA,
                        ZoneABCbis.ZoneB1,
                        ZoneABCbis.ZoneB2,
                        ZoneABCbis.ZoneC,
                    ]
                ).value,
                "type_habitat": random.choice(
                    [
                        TypeHabitat.COLLECTIF,
                        TypeHabitat.INDIVIDUEL,
                        TypeHabitat.MIXTE,
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

        administration_test, _ = Administration.objects.get_or_create(**administration)
        bailleur_test, _ = Bailleur.objects.get_or_create(**bailleur)
        for programme in generate_programmes(30):
            lots = programme.pop("lots")
            programme_test, _ = Programme.objects.get_or_create(
                **programme, administration=administration_test, bailleur=bailleur_test
            )
            for lot in lots:
                Lot.objects.get_or_create(
                    **lot, programme=programme_test, bailleur=bailleur_test
                )
