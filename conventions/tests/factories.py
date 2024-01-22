import factory

from conventions.models import Convention
from core.tests.factories import BaseFactory
from upload.tests.factories import UploadFactoryMixin


class ConventionFactory(BaseFactory, UploadFactoryMixin):
    class Meta:
        model = Convention

    numero = factory.Sequence(lambda n: f"Convention {n}")

    lot = factory.SubFactory("programmes.tests.factories.LotFactory")
    programme = factory.SelfAttribute("lot.programme")
    financement = factory.SelfAttribute("lot.financement")
