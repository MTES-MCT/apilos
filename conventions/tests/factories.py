import factory

from conventions.models import AvenantType, Convention
from core.tests.factories import BaseFactory
from programmes.tests.factories import LotFactory, ProgrammeFactory
from upload.tests.factories import UploadFactoryMixin


class ConventionFactory(BaseFactory, UploadFactoryMixin):
    class Meta:
        model = Convention
        skip_postgeneration_save = True

    class Params:
        create_lot = False

    numero = factory.Sequence(lambda n: f"Convention {n}")
    programme = factory.SubFactory(ProgrammeFactory)

    # lot = factory.SubFactory("programmes.tests.factories.LotFactory")
    # programme = factory.SelfAttribute("lot.programme")
    # financement = factory.SelfAttribute("lot.financement")

    @factory.post_generation
    def create_lot(obj, create, extracted, **kwargs):  # noqa: N805
        if not create:
            return
        if obj.create_lot:
            lot = LotFactory.create(convention=obj, programme=obj.programme)
            obj.financement = lot.financement
            obj.save()


class AvenantFactory(ConventionFactory):
    numero = "1"
    parent = factory.SubFactory(ConventionFactory)


class AvenantTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AvenantType
        django_get_or_create = ("nom",)
