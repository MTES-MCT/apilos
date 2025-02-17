import factory

from conventions.models import AvenantType, Convention
from core.tests.factories import BaseFactory
from programmes.tests.factories import LotFactory, ProgrammeFactory
from upload.tests.factories import UploadFactoryMixin


class ConventionFactory(BaseFactory, UploadFactoryMixin):
    class Meta:
        model = Convention
        skip_postgeneration_save = True

    numero = factory.Sequence(lambda n: f"Convention {n}")
    programme = factory.SubFactory(ProgrammeFactory)

    @factory.post_generation
    def create_lot(obj, create, extracted, **kwargs):  # noqa: N805
        if extracted and create:
            lot = LotFactory.create(convention=obj, programme=obj.programme, **kwargs)
            obj.financement = lot.financement
            obj.save()


class AvenantFactory(ConventionFactory):
    numero = "1"
    parent = factory.SubFactory(ConventionFactory)

    @factory.post_generation
    def create_lot(obj, create, extracted, **kwargs):  # noqa: N805
        if extracted and create:
            lot = LotFactory.create(convention=obj, programme=obj.programme, **kwargs)
            obj.financement = lot.financement
            obj.save()


class AvenantTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AvenantType
        django_get_or_create = ("nom",)
