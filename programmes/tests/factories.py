import json
import uuid
from datetime import date

import factory
from factory import fuzzy

from apilos_settings.models import Departement
from core.tests.factories import BaseFactory
from programmes.models import Annexe, Logement, Lot, Programme
from programmes.models.choices import (
    Financement,
    TypeHabitat,
    TypologieAnnexe,
    TypologieLogement,
)
from upload.tests.factories import UploadFactoryMixin


class ProgrammeFactory(BaseFactory, UploadFactoryMixin):
    class Meta:
        model = Programme

    nom = factory.Sequence(lambda n: f"Programme {n}")
    numero_operation = factory.LazyFunction(lambda: str(uuid.uuid4().int)[:13])

    bailleur = factory.SubFactory("bailleurs.tests.factories.BailleurFactory")
    administration = factory.SubFactory(
        "instructeurs.tests.factories.AdministrationFactory"
    )

    ville = "Paris"
    code_postal = "75007"
    code_insee_departement = factory.LazyAttribute(lambda o: o.code_postal[0:2])
    adresse = "22 rue segur"
    annee_gestion_programmation = 2018
    zone_123 = "3"
    zone_abc = "B1"
    surface_utile_totale = 5243.21
    nb_locaux_commerciaux = 5
    nb_bureaux = 25
    autres_locaux_hors_convention = "quelques uns"
    permis_construire = "123 456 789 ABC"
    date_achevement_previsible = date(2024, 1, 2)
    date_achat = date(2022, 1, 2)
    date_achevement = date(2024, 4, 11)
    edd_stationnements = factory.LazyFunction(
        lambda: json.dumps(
            {
                "text": "EDD stationnements",
                "files": {
                    "fbb9890f-171b-402d-a35e-71e1bd791b70": {
                        "uuid": "fbb9890f-171b-402d-a35e-71e1bd791b70",
                        "thumbnail": "data:image/png;base64,BLAHBLAH==",
                        "size": "31185",
                        "filename": "acquereur1.png",
                        "content_type": "image/png",
                    },
                    "dccd310d-2e50-45d8-a477-db7b08ae1d71": {
                        "uuid": "dccd310d-2e50-45d8-a477-db7b08ae1d71",
                        "thumbnail": "data:image/png;base64,BLIHBLIH==",
                        "size": "69076",
                        "filename": "acquereur2.png",
                        "content_type": "image/png",
                    },
                },
            }
        )
    )


class LogementFactory(BaseFactory):
    class Meta:
        model = Logement

    designation = factory.Faker("word", locale="fr_FR")
    typologie = fuzzy.FuzzyChoice(TypologieLogement)

    surface_habitable = 50
    surface_annexes = 20
    surface_annexes_retenue = 10
    surface_utile = 60
    loyer_par_metre_carre = 5.5
    coeficient = 0.9
    loyer = 60 * 5.5 * 0.9

    lot = factory.SubFactory("programmes.tests.factories.LotFactory")


class LotFactory(BaseFactory, UploadFactoryMixin):
    class Meta:
        model = Lot

    financement = fuzzy.FuzzyChoice(Financement)
    type_habitat = fuzzy.FuzzyChoice(TypeHabitat)

    programme = factory.SubFactory(ProgrammeFactory)


class AnnexeFactory(BaseFactory):
    class Meta:
        model = Annexe

    typologie = fuzzy.FuzzyChoice(TypologieAnnexe)
    surface_hors_surface_retenue = fuzzy.FuzzyDecimal(1.0, 20.0)
    loyer_par_metre_carre = fuzzy.FuzzyDecimal(0.1, 1.0)
    loyer = factory.LazyAttribute(
        lambda o: o.surface_hors_surface_retenue * o.loyer_par_metre_carre
    )

    logement = factory.SubFactory(LogementFactory)


class DepartementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Departement
        django_get_or_create = ("code_insee", "nom")
