import factory
from django.contrib.auth.models import Group, Permission

from users.models import Role, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.Faker("password")
    first_name = factory.Faker("first_name", locale="fr_FR")
    last_name = factory.Faker("last_name", locale="fr_FR")
    telephone = factory.Faker("phone_number", locale="fr_FR")

    class Params:
        cerbere = factory.Trait(cerbere_login=factory.SelfAttribute("email"))


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ("name",)
        skip_postgeneration_save = True

    name = factory.Faker("word")

    @factory.post_generation
    def rwd(instance, create, extracted, **kwargs):  # noqa: N805
        if extracted:
            perms = []
            for obj in extracted:
                perms += [
                    Permission.objects.get(
                        content_type__model=obj, codename=f"{prefix}_{obj}"
                    )
                    for prefix in ("add", "change", "delete", "view")
                ]
            instance.permissions.add(*perms)

    @factory.post_generation
    def rw(instance, create, extracted, **kwargs):  # noqa: N805
        if extracted:
            perms = []
            for obj in extracted:
                perms += [
                    Permission.objects.get(
                        content_type__model=obj, codename=f"{prefix}_{obj}"
                    )
                    for prefix in ("add", "change", "view")
                ]
            instance.permissions.add(*perms)

    @factory.post_generation
    def ru(instance, create, extracted, **kwargs):  # noqa: N805
        if extracted:
            perms = []
            for obj in extracted:
                perms += [
                    Permission.objects.get(
                        content_type__model=obj, codename=f"{prefix}_{obj}"
                    )
                    for prefix in ("change", "view")
                ]
            instance.permissions.add(*perms)

    @factory.post_generation
    def ro(instance, create, extracted, **kwargs):  # noqa: N805
        if extracted:
            perms = [
                Permission.objects.get(content_type__model=obj, codename=f"view_{obj}")
                for obj in extracted
            ]
            instance.permissions.add(*perms)
