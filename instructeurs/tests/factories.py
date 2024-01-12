import factory

from core.tests.factories import BaseFactory
from instructeurs.models import Administration


class AdministrationFactory(BaseFactory):
    class Meta:
        model = Administration
        django_get_or_create = ("code",)

    nom = factory.Faker("company", locale="fr_FR")
    code = factory.Sequence(lambda n: f"{n:05d}")
