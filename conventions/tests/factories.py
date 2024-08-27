import factory

from conventions.models import AvenantType, Convention
from core.tests.factories import BaseFactory
from upload.tests.factories import UploadFactoryMixin


class ConventionFactory(BaseFactory, UploadFactoryMixin):
    class Meta:
        model = Convention
        skip_postgeneration_save = True

    numero = factory.Sequence(lambda n: f"Convention {n}")

    lot = factory.SubFactory("programmes.tests.factories.LotFactory")
    programme = factory.SelfAttribute("lot.programme")
    financement = factory.SelfAttribute("lot.financement")


class AvenantFactory(ConventionFactory):
    numero = "1"
    parent = factory.SubFactory(ConventionFactory)


class AvenantTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AvenantType
        django_get_or_create = ("nom",)
