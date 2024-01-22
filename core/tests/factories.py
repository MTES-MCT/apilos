import uuid

import factory


class BaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    uuid = factory.LazyFunction(uuid.uuid4)
