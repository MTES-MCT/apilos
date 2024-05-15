import pytest
from django.conf import settings
from django.core.management import call_command
from django.db.models.functions import Substr
from django.test import TestCase
from django.test.client import RequestFactory
from waffle.testutils import override_switch

from apilos_settings.models import Departement
from bailleurs.models import Bailleur
from bailleurs.tests.factories import BailleurFactory
from conventions.models import Convention, ConventionStatut
from conventions.services.avenants import create_avenant
from conventions.tests.factories import ConventionFactory
from programmes.models import Programme
from users.models import ExceptionPermissionConfig, Role, User
from users.tests.factories import GroupFactory, UserFactory
from users.type_models import TypeRole


class TestUserIsAdmin:
    def test_user_is_not_admin(self):
        user = UserFactory.build()
        assert not user.is_admin

    def test_staff_user_is_admin(self):
        user = UserFactory.build(is_staff=True)
        assert user.is_admin

    def test_superuser_is_admin(self):
        user = UserFactory.build(is_superuser=True)
        assert user.is_admin


class UserModelStrTest(TestCase):
    # Test model User
    def test_object_user_str(self):
        user = User(
            username="adupont",
            email="antoine.dupont@ffr.fr",
            first_name="Antoine",
            last_name="Dupont",
        )
        self.assertEqual(str(user), "Antoine Dupont")
        user.first_name = ""
        self.assertEqual(str(user), "Dupont")
        user.last_name = ""
        user.first_name = "Antoine"
        self.assertEqual(str(user), "Antoine")
        user.last_name = ""
        user.first_name = ""
        self.assertEqual(str(user), "adupont")


class UserPermissions(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_exception_permissions(self):
        user_instructeur = User.objects.get(username="sabine")
        for perm in ["convention.view_convention", "convention.change_convention"]:
            with self.assertRaises(ExceptionPermissionConfig):
                # has_perm with non convention object should raise an Exception
                user_instructeur.has_perm(perm, user_instructeur)

    def test_permissions_instructeur(self):
        user_instructeur_paris = User.objects.get(username="fix")
        user_instructeur_metropole = User.objects.get(username="roger")

        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.PROJET.label
        self.assertTrue(
            user_instructeur_paris.has_perm("convention.change_convention", convention)
        )
        self.assertTrue(
            user_instructeur_paris.has_perm("convention.change_convention", convention)
        )
        self.assertFalse(
            user_instructeur_metropole.has_perm(
                "convention.change_convention", convention
            )
        )
        self.assertTrue(
            user_instructeur_paris.has_perm("convention.view_convention", convention)
        )
        self.assertTrue(user_instructeur_paris.has_perm("convention.add_convention"))
        self.assertTrue(
            user_instructeur_paris.has_perm("convention.add_convention", convention.lot)
        )
        self.assertFalse(
            user_instructeur_metropole.has_perm(
                "convention.view_convention", convention
            )
        )
        self.assertTrue(
            user_instructeur_metropole.has_perm("convention.add_convention")
        )
        self.assertFalse(
            user_instructeur_metropole.has_perm(
                "convention.add_convention", convention.lot
            )
        )
        for statut in [
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
        ]:
            convention.statut = statut
            self.assertTrue(
                user_instructeur_paris.has_perm(
                    "convention.change_convention", convention
                )
            )
            self.assertFalse(
                user_instructeur_metropole.has_perm(
                    "convention.change_convention", convention
                )
            )
            self.assertTrue(
                user_instructeur_paris.has_perm(
                    "convention.view_convention", convention
                )
            )
            self.assertFalse(
                user_instructeur_metropole.has_perm(
                    "convention.view_convention", convention
                )
            )

    def test_permissions_bailleur(self):
        user_bailleur = User.objects.get(username="raph")
        user_bailleur_hlm = User.objects.get(username="sophie")

        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.PROJET.label
        self.assertFalse(
            user_bailleur_hlm.has_perm("convention.change_convention", convention)
        )
        self.assertTrue(
            user_bailleur.has_perm("convention.view_convention", convention)
        )
        self.assertFalse(
            user_bailleur_hlm.has_perm("convention.view_convention", convention)
        )
        self.assertTrue(user_bailleur.has_perm("convention.add_convention"))
        self.assertTrue(
            user_bailleur.has_perm("convention.add_convention", convention.lot)
        )
        self.assertTrue(user_bailleur_hlm.has_perm("convention.add_convention"))
        self.assertFalse(
            user_bailleur_hlm.has_perm("convention.add_convention", convention.lot)
        )
        for statut in [
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
        ]:
            convention.statut = statut
            self.assertTrue(
                user_bailleur.has_perm("convention.change_convention", convention)
            )
            self.assertFalse(
                user_bailleur_hlm.has_perm("convention.change_convention", convention)
            )
            self.assertTrue(
                user_bailleur.has_perm("convention.view_convention", convention)
            )
            self.assertFalse(
                user_bailleur_hlm.has_perm("convention.view_convention", convention)
            )


class UserQuerySetTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_programmes(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(
            list(user_superuser.programmes().values_list("uuid", flat=True)),
            list(Programme.objects.all().values_list("uuid", flat=True)),
        )
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(
            list(user_instructeur.programmes().values_list("uuid", flat=True)),
            list(
                Programme.objects.filter(
                    administration_id__in=[
                        user_instructeur.roles.all()[0].administration_id,
                        user_instructeur.roles.all()[1].administration_id,
                    ]
                ).values_list("uuid", flat=True)
            ),
        )
        user_bailleur = User.objects.get(username="raph")
        programme_id_list = list(
            Programme.objects.filter(
                bailleur_id__in=[
                    user_bailleur.roles.all()[0].bailleur_id,
                    user_bailleur.roles.all()[1].bailleur_id,
                ]
            ).values_list("uuid", flat=True)
        )
        self.assertEqual(
            list(user_bailleur.programmes().values_list("uuid", flat=True)),
            programme_id_list,
        )
        user_bailleur.filtre_departements.add(Departement.objects.get(code_insee="13"))
        programme_id_list_with_filters = list(
            Programme.objects.annotate(departement=Substr("code_postal", 1, 2))
            .filter(
                bailleur_id__in=[
                    user_bailleur.roles.all()[0].bailleur_id,
                    user_bailleur.roles.all()[1].bailleur_id,
                ],
                departement="13",
            )
            .values_list("uuid", flat=True)
        )
        self.assertEqual(
            list(user_bailleur.programmes().values_list("uuid", flat=True)),
            programme_id_list_with_filters,
        )
        self.assertNotEqual(
            programme_id_list,
            programme_id_list_with_filters,
        )

    def test_administration_filter(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(user_superuser.administration_filter(), {})
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(
            user_instructeur.administration_filter(),
            {
                "id__in": [
                    user_instructeur.roles.all()[0].administration_id,
                    user_instructeur.roles.all()[1].administration_id,
                ]
            },
        )
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(user_bailleur.administration_filter(), {"id__in": []})

    def test_bailleur_filter(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(user_superuser.bailleur_filter(), {})
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(user_instructeur.bailleur_filter(), {"id__in": []})
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(
            user_bailleur.bailleur_filter(),
            {
                "id__in": [
                    user_bailleur.roles.all()[0].bailleur_id,
                    user_bailleur.roles.all()[1].bailleur_id,
                ]
            },
        )

    def test_conventions(self):
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(
            {convention.uuid for convention in user_instructeur.conventions()},
            {
                convention.uuid
                for convention in Convention.objects.filter(
                    programme__administration_id__in=[
                        user_instructeur.roles.all()[0].administration_id,
                        user_instructeur.roles.all()[1].administration_id,
                    ]
                )
            },
        )
        user_bailleur = User.objects.get(username="raph")
        convention_id_list = {
            convention.uuid
            for convention in Convention.objects.filter(
                programme__bailleur_id__in=[
                    user_bailleur.roles.all()[0].bailleur_id,
                    user_bailleur.roles.all()[1].bailleur_id,
                ]
            )
        }
        self.assertEqual(
            {convention.uuid for convention in user_bailleur.conventions()},
            convention_id_list,
        )
        user_bailleur.filtre_departements.add(Departement.objects.get(code_insee="13"))
        convention_id_list_with_filters = {
            convention.uuid
            for convention in Convention.objects.annotate(
                departement=Substr("programme__code_postal", 1, 2)
            ).filter(
                programme__bailleur_id__in=[
                    user_bailleur.roles.all()[0].bailleur_id,
                    user_bailleur.roles.all()[1].bailleur_id,
                ],
                departement="13",
            )
        }
        self.assertEqual(
            {convention.uuid for convention in user_bailleur.conventions()},
            convention_id_list_with_filters,
        )
        self.assertNotEqual(
            convention_id_list,
            convention_id_list_with_filters,
        )

    def test_user_list(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(
            user_superuser.user_list(order_by="username").first(),
            User.objects.all().order_by("username").first(),
        )
        self.assertEqual(
            user_superuser.user_list(order_by="username").last(),
            User.objects.all().order_by("username").last(),
        )
        self.assertEqual(
            user_superuser.user_list(order_by="username").count(),
            User.objects.all().order_by("username").count(),
        )
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(user_instructeur.user_list().count(), 2)
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(user_bailleur.user_list().count(), 2)

    # Test model Role
    def test_object_role_str(self):
        role = User.objects.get(username="sabine").roles.all()[0]
        expected_object_name = f"{role.user} - {role.typologie} - {role.administration}"
        self.assertEqual(str(role), expected_object_name)


class UserBailleurQuerySetTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        troisf = Bailleur.objects.get(nom="3F")
        hlm = Bailleur.objects.get(nom="HLM")
        troisf.parent = hlm
        troisf.save()

    def test_bailleur_queryset_bailleur(self):
        user = User.objects.get(username="raph")
        bailleurs = user.bailleurs().filter(parent=None)
        self.assertEqual(set(user.bailleur_query_set()), set(bailleurs))

    def test_bailleur_queryset_instructeur(self):
        user = User.objects.get(username="sabine")
        bailleurs = Bailleur.objects.all().filter(parent=None)
        self.assertEqual(set(user.bailleur_query_set()), set(bailleurs))

    def test_bailleur_queryset_bailleur_only(self):
        user = User.objects.get(username="raph")
        bailleur = user.bailleurs().filter(parent=None).first()
        self.assertEqual(
            set(user.bailleur_query_set(only_bailleur_uuid=bailleur.uuid)),
            set([bailleur]),
        )

    def test_bailleur_queryset_bailleur_exclude(self):
        user = User.objects.get(username="raph")
        bailleur = user.bailleurs().filter(parent=None).first()
        bailleurs = user.bailleurs().filter(parent=None).exclude(uuid=bailleur.uuid)

        self.assertEqual(
            set(user.bailleur_query_set(exclude_bailleur_uuid=bailleur.uuid)),
            set(bailleurs),
        )

    def test_bailleur_queryset_bailleur_querystring(self):
        user = User.objects.get(username="raph")
        bailleurs = user.bailleurs().filter(nom__contains="HL")
        self.assertEqual(
            set(user.bailleur_query_set(query_string="hl", has_no_parent=False)),
            set(bailleurs),
        )

    def test_bailleur_queryset_bailleur_noparent(self):
        user = User.objects.get(username="raph")
        bailleurs = user.bailleurs()
        self.assertEqual(
            set(user.bailleur_query_set(has_no_parent=False)),
            set(bailleurs),
        )


def _create_bailleur_and_user(group):
    bailleur = BailleurFactory()
    user = UserFactory()

    Role.objects.create(
        typologie=TypeRole.BAILLEUR,
        bailleur=bailleur,
        user=user,
        group=group,
    )
    return bailleur, user


@pytest.fixture
def load_avenant_types(db):
    call_command("loaddata", "avenant_types.json")


@override_switch(settings.SWITCH_VISIBILITY_AVENANT_BAILLEUR, active=True)
def test_conventions_visibility_bailleur_avenant(db, load_avenant_types):
    # Create three bailleurs
    super_user = UserFactory(is_staff=True, is_superuser=True)
    group = GroupFactory(name="Bailleur", rw=[])
    bailleur1, user1 = _create_bailleur_and_user(group)
    bailleur2, user2 = _create_bailleur_and_user(group)
    bailleur3, user3 = _create_bailleur_and_user(group)

    # Create two conventions for the first bailleur
    convention1 = ConventionFactory()
    convention1.programme.bailleur = bailleur1
    convention1.programme.save()
    convention2 = ConventionFactory()
    convention2.programme.bailleur = bailleur1
    convention2.programme.save()

    assert user1.conventions().count() == 2
    assert user2.conventions().count() == 0
    assert user3.conventions().count() == 0

    # Make an avenant on the first convention
    request = RequestFactory().post("/", data={"avenant_type": "resiliation"})
    request.user = super_user
    result = create_avenant(request, convention1.uuid)
    avenant1 = result["convention"]
    avenant1.statut = ConventionStatut.SIGNEE.label
    avenant1.save()

    assert user1.conventions().count() == 3
    assert user2.conventions().count() == 0
    assert user3.conventions().count() == 0

    assert user1.has_object_permission(convention1)
    assert user1.has_object_permission(avenant1)
    assert not user2.has_object_permission(convention1)
    assert not user2.has_object_permission(avenant1)

    # Make another avenant in statut PROJET on the first convention changing bailleur
    request = RequestFactory().post("/", data={"avenant_type": "bailleur"})
    request.user = super_user
    result = create_avenant(request, convention1.uuid)
    avenant2 = result["convention"]
    avenant2.statut = ConventionStatut.PROJET.label
    avenant2.save()

    avenant2.programme.bailleur = bailleur2
    avenant2.programme.save()

    assert user1.conventions().count() == 4
    assert user2.conventions().count() == 0
    assert user3.conventions().count() == 0

    assert user1.has_object_permission(convention1)
    assert user1.has_object_permission(avenant1)
    assert user1.has_object_permission(avenant2)
    assert not user2.has_object_permission(convention1)
    assert not user2.has_object_permission(avenant1)
    assert not user2.has_object_permission(avenant2)

    avenant2.statut = ConventionStatut.CORRECTION.label
    avenant2.save()

    assert user1.conventions().count() == 1
    assert user2.conventions().count() == 3
    assert user3.conventions().count() == 0

    assert not user1.has_object_permission(convention1)
    assert not user1.has_object_permission(avenant1)
    assert not user1.has_object_permission(avenant2)
    assert user2.has_object_permission(convention1)
    assert user2.has_object_permission(avenant1)
    assert user2.has_object_permission(avenant2)

    # Verify that the bailleur_id from the first avenant is not impacting visibility
    avenant1.programme.bailleur = bailleur3
    avenant1.programme.save()

    assert user1.conventions().count() == 1
    assert user2.conventions().count() == 3
    assert user3.conventions().count() == 0
