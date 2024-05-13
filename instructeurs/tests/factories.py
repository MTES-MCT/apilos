import factory

from core.tests.factories import BaseFactory
from instructeurs.models import Administration


class AdministrationFactory(BaseFactory):
    class Meta:
        model = Administration
        django_get_or_create = ("code",)

    nom = factory.Faker("company", locale="fr_FR")
    code = factory.Sequence(lambda n: f"{n:05d}")
    adresse = factory.Faker("address", locale="fr_FR")
    code_postal = factory.Faker("postcode", locale="fr_FR")
    ville = factory.Faker("city", locale="fr_FR")
    ville_signature = factory.Faker("city", locale="fr_FR")
    nb_convention_exemplaires = 3
