from django.test import TestCase

from core.tests import utils_fixtures
from users.models import User, Role
from users.type_models import TypeRole
from conventions.models import Convention, ConventionStatut
from programmes.models import Financement


class AdministrationsModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_users_superuser()
        (
            user_instructeur,
            user_instructeur_metropole,
        ) = utils_fixtures.create_users_instructeur()
        (user_bailleur, user_bailleur_hlm) = utils_fixtures.create_users_bailleur()
        (
            administration,
            administration_metropole,
        ) = utils_fixtures.create_administrations()
        (bailleur, bailleur_hlm) = utils_fixtures.create_bailleurs()
        group_instructeur = utils_fixtures.create_group(
            "Instructeur", rwd=["logement", "convention"]
        )
        group_bailleur = utils_fixtures.create_group(
            "Bailleur", rw=["logement", "convention"]
        )

        Role.objects.create(
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=user_bailleur,
            group=group_bailleur,
        )
        Role.objects.create(
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur_hlm,
            user=user_bailleur_hlm,
            group=group_bailleur,
        )
        Role.objects.create(
            typologie=TypeRole.INSTRUCTEUR,
            administration=administration,
            user=user_instructeur,
            group=group_instructeur,
        )
        Role.objects.create(
            typologie=TypeRole.INSTRUCTEUR,
            administration=administration_metropole,
            user=user_instructeur_metropole,
            group=group_instructeur,
        )
        programme = utils_fixtures.create_programme(
            bailleur, administration, nom="Programe 1"
        )
        lot_plai = utils_fixtures.create_lot(programme, Financement.PLAI)
        lot_plus = utils_fixtures.create_lot(programme, Financement.PLUS)
        utils_fixtures.create_convention(lot_plus, numero="0001")
        utils_fixtures.create_convention(lot_plai, numero="0002")

    # Test model User
    def test_object_user_str(self):
        user = User.objects.get(username="sabine")
        expected_object_name = f"{user.first_name} {user.last_name}"
        self.assertEqual(str(user), expected_object_name)
        user.first_name = ""
        expected_object_name = f"{user.last_name}"
        self.assertEqual(str(user), expected_object_name)
        user.last_name = ""
        user.first_name = "Sabine"
        expected_object_name = f"{user.first_name}"
        self.assertEqual(str(user), expected_object_name)
        user.last_name = ""
        user.first_name = ""
        expected_object_name = f"{user.username}"
        self.assertEqual(str(user), expected_object_name)

    def test_is_role(self):
        user_instructeur = User.objects.get(username="sabine")
        self.assertTrue(user_instructeur.is_instructeur())
        self.assertFalse(user_instructeur.is_bailleur())
        user_bailleur = User.objects.get(username="raph")
        self.assertFalse(user_bailleur.is_instructeur())
        self.assertTrue(user_bailleur.is_bailleur())

    def test_exception_permissions(self):
        # pylint: disable=W0703
        user_instructeur = User.objects.get(username="sabine")
        for perm in ["convention.view_convention", "convention.change_convention"]:
            try:
                user_instructeur.has_perm(perm, user_instructeur)
                self.fail(
                    f"has_perm '{perm}' "
                    + "with non convention object shold raise an Exception"
                )
            except Exception:
                pass

    def test_permissions(self):
        user_instructeur = User.objects.get(username="sabine")
        user_instructeur_metropole = User.objects.get(username="roger")
        self.assertTrue(user_instructeur.has_perm("logement.change_logement"))
        self.assertTrue(user_instructeur.has_perm("logement.delete_logement"))
        self.assertFalse(user_instructeur.has_perm("bailleur.delete_bailleur"))

        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.BROUILLON
        self.assertFalse(user_instructeur.full_editable_convention(convention))
        self.assertFalse(
            user_instructeur_metropole.full_editable_convention(convention)
        )
        self.assertTrue(
            user_instructeur.has_perm("convention.change_convention", convention)
        )
        self.assertTrue(
            user_instructeur.has_perm("convention.change_convention", convention)
        )
        self.assertFalse(
            user_instructeur_metropole.has_perm(
                "convention.change_convention", convention
            )
        )
        self.assertTrue(
            user_instructeur.has_perm("convention.view_convention", convention)
        )
        self.assertTrue(user_instructeur.has_perm("convention.add_convention"))
        self.assertTrue(
            user_instructeur.has_perm("convention.add_convention", convention.lot)
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
        for statut in [ConventionStatut.INSTRUCTION, ConventionStatut.CORRECTION]:
            convention.statut = statut
            self.assertTrue(user_instructeur.full_editable_convention(convention))
            self.assertFalse(
                user_instructeur_metropole.full_editable_convention(convention)
            )
            self.assertTrue(
                user_instructeur.has_perm("convention.change_convention", convention)
            )
            self.assertFalse(
                user_instructeur_metropole.has_perm(
                    "convention.change_convention", convention
                )
            )
            self.assertTrue(
                user_instructeur.has_perm("convention.view_convention", convention)
            )
            self.assertFalse(
                user_instructeur_metropole.has_perm(
                    "convention.view_convention", convention
                )
            )

        user_bailleur = User.objects.get(username="raph")
        user_bailleur_hlm = User.objects.get(username="sophie")
        self.assertTrue(user_bailleur.has_perm("logement.change_logement"))
        self.assertFalse(user_bailleur.has_perm("logement.delete_logement"))
        self.assertFalse(user_bailleur.has_perm("bailleur.delete_bailleur"))

        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.BROUILLON
        self.assertTrue(user_bailleur.full_editable_convention(convention))
        self.assertFalse(user_bailleur_hlm.full_editable_convention(convention))
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
        self.assertTrue(user_bailleur.has_perm("convention.add_convention"))
        self.assertTrue(
            user_bailleur.has_perm("convention.add_convention", convention.lot)
        )
        self.assertTrue(user_bailleur_hlm.has_perm("convention.add_convention"))
        self.assertFalse(
            user_bailleur_hlm.has_perm("convention.add_convention", convention.lot)
        )
        for statut in [ConventionStatut.INSTRUCTION, ConventionStatut.CORRECTION]:
            convention.statut = statut
            self.assertFalse(user_bailleur.full_editable_convention(convention))
            self.assertFalse(user_bailleur_hlm.full_editable_convention(convention))
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

    def test_programme_filter(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(user_superuser.programme_filter(), {})
        self.assertEqual(user_superuser.programme_filter(prefix="programme__"), {})
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(
            user_instructeur.programme_filter(),
            {
                "administration_id__in": [
                    user_instructeur.role_set.all()[0].administration_id
                ]
            },
        )
        self.assertEqual(
            user_instructeur.programme_filter(prefix="programme__"),
            {
                "programme__administration_id__in": [
                    user_instructeur.role_set.all()[0].administration_id
                ]
            },
        )
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(
            user_bailleur.programme_filter(),
            {"bailleur_id__in": [user_bailleur.role_set.all()[0].bailleur_id]},
        )
        self.assertEqual(
            user_bailleur.programme_filter(prefix="programme__"),
            {
                "programme__bailleur_id__in": [
                    user_bailleur.role_set.all()[0].bailleur_id
                ]
            },
        )

    def test_administration_filter(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(user_superuser.administration_filter(), {})
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(
            user_instructeur.administration_filter(),
            {"id__in": [user_instructeur.role_set.all()[0].administration_id]},
        )
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(user_bailleur.administration_filter(), {})

    def test_administration_ids(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(user_superuser.administration_ids(), [])
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(
            user_instructeur.administration_ids(),
            [user_instructeur.role_set.all()[0].administration_id],
        )
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(user_bailleur.administration_ids(), [])

    def test_bailleur_filter(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(user_superuser.bailleur_filter(), {})
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(user_instructeur.bailleur_filter(), {})
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(
            user_bailleur.bailleur_filter(),
            {"id__in": [user_bailleur.role_set.all()[0].bailleur_id]},
        )

    def test_bailleur_ids(self):
        user_superuser = User.objects.get(username="nicolas")
        self.assertEqual(user_superuser.bailleur_ids(), [])
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(user_instructeur.bailleur_ids(), [])
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(
            user_bailleur.bailleur_ids(),
            [user_bailleur.role_set.all()[0].bailleur_id],
        )

    def test_convention_filter(self):
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(
            user_instructeur.convention_filter(),
            {
                "programme__administration_id__in": [
                    user_instructeur.role_set.all()[0].administration_id
                ]
            },
        )
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(
            user_bailleur.convention_filter(),
            {"bailleur_id__in": [user_bailleur.role_set.all()[0].bailleur_id]},
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
        self.assertEqual(user_instructeur.user_list().count(), 1)
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(user_bailleur.user_list().count(), 1)

    # Test model Role
    def test_object_role_str(self):
        role = User.objects.get(username="sabine").role_set.all()[0]
        expected_object_name = f"{role.user} - {role.typologie} - {role.administration}"
        self.assertEqual(str(role), expected_object_name)
