import datetime
from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from core.tests import utils
from users.models import User, Role
from bailleurs.models import Bailleur
from instructeurs.models import Administration
from conventions.models import Convention, ConventionStatut
from programmes.models import Lot, Financement


class AdministrationsModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_instructeur = User.objects.create(
            username="sabine",
            password="12345",
            first_name="Sabine",
            last_name="Marini",
            email="sabine@apilos.fr",
        )
        user_instructeur_metropole = User.objects.create(
            username="roger",
            password="567890",
            first_name="Roger",
            last_name="Dupont",
            email="roger@apilos.fr",
        )
        user_bailleur = User.objects.create(
            username="raph",
            password="12345",
            first_name="Raphaëlle",
            last_name="Neyton",
            email="raph@apilos.fr",
        )
        user_bailleur_hlm = User.objects.create(
            username="sophie",
            password="567890",
            first_name="Sophie",
            last_name="Eaubonne",
            email="sophie@apilos.fr",
        )
        administration = Administration.objects.create(
            nom="CA d'Arles-Crau-Camargue-Montagnette",
            code="12345",
        )
        administration_metropole = Administration.objects.create(
            nom="Métroploe de Marseille",
            code="67890",
        )
        bailleur = utils.create_bailleur()
        bailleur_hlm = Bailleur.objects.create(
            nom="HLM",
            siret="987654321",
            capital_social="123456",
            ville="Marseille",
            dg_nom="Pall Antoine",
            dg_fonction="DG",
            dg_date_deliberation=datetime.date(2001, 12, 1),
        )
        group_instructeur = Group.objects.create(
            name="Instructeur",
        )
        group_instructeur.permissions.set(
            [
                Permission.objects.get(
                    content_type__model="logement", codename="add_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="change_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="delete_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="view_logement"
                ),
                Permission.objects.get(
                    content_type__model="convention", codename="add_convention"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="change_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="delete_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="view_logement"
                ),
            ]
        )
        group_bailleur = Group.objects.create(
            name="Bailleur",
        )
        group_bailleur.permissions.set(
            [
                Permission.objects.get(
                    content_type__model="logement", codename="add_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="change_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="view_logement"
                ),
                Permission.objects.get(
                    content_type__model="convention", codename="add_convention"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="change_logement"
                ),
                Permission.objects.get(
                    content_type__model="logement", codename="view_logement"
                ),
            ]
        )
        Role.objects.create(
            typologie=Role.TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=user_bailleur,
            group=group_bailleur,
        )
        Role.objects.create(
            typologie=Role.TypeRole.BAILLEUR,
            bailleur=bailleur_hlm,
            user=user_bailleur_hlm,
            group=group_bailleur,
        )
        Role.objects.create(
            typologie=Role.TypeRole.INSTRUCTEUR,
            administration=administration,
            user=user_instructeur,
            group=group_instructeur,
        )
        Role.objects.create(
            typologie=Role.TypeRole.INSTRUCTEUR,
            administration=administration_metropole,
            user=user_instructeur_metropole,
            group=group_instructeur,
        )
        programme = utils.create_programme(bailleur, administration)
        lot = Lot.objects.create(
            programme=programme,
            bailleur=bailleur,
            financement=Financement.PLAI,
        )
        Convention.objects.create(
            numero="0001",
            lot=lot,
            programme=programme,
            bailleur=bailleur,
            financement=Financement.PLUS,
        )
        Convention.objects.create(
            numero="0002",
            lot=lot,
            programme=programme,
            bailleur=bailleur,
            financement=Financement.PLAI,
        )

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
        convention.statut = ConventionStatut.INSTRUCTION
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
        convention.statut = ConventionStatut.INSTRUCTION
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
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(user_instructeur.programme_filter(), {})
        user_bailleur = User.objects.get(username="raph")
        self.assertEqual(
            user_bailleur.programme_filter(),
            {"bailleur_id__in": [user_bailleur.role_set.all()[0].bailleur_id]},
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

    # Test model Role
    def test_object_role_str(self):
        role = User.objects.get(username="sabine").role_set.all()[0]
        expected_object_name = f"{role.user} - {role.typologie} - {role.administration}"
        self.assertEqual(str(role), expected_object_name)
