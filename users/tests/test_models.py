from django.db.models.functions import Substr
from django.test import TestCase
from bailleurs.models import Bailleur

from apilos_settings.models import Departement
from instructeurs.models import Administration
from conventions.models import Convention, ConventionStatut
from programmes.models import Programme
from users.models import User


class AdministrationsModelsTest(TestCase):
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
        user_instructeur_paris = User.objects.get(username="fix")
        user_instructeur_metropole = User.objects.get(username="roger")
        self.assertTrue(user_instructeur_paris.has_perm("logement.change_logement"))
        self.assertTrue(user_instructeur_paris.has_perm("logement.delete_logement"))
        self.assertFalse(user_instructeur_paris.has_perm("bailleur.delete_bailleur"))

        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.PROJET
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
        for statut in [ConventionStatut.INSTRUCTION, ConventionStatut.CORRECTION]:
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

        user_bailleur = User.objects.get(username="raph")
        user_bailleur_hlm = User.objects.get(username="sophie")
        self.assertTrue(user_bailleur.has_perm("logement.change_logement"))
        self.assertTrue(user_bailleur.has_perm("logement.delete_logement"))
        self.assertFalse(user_bailleur.has_perm("bailleur.delete_bailleur"))

        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.PROJET
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

    def test_is_administrator(self):
        user_superuser = User.objects.get(username="nicolas")
        user_instructeur = User.objects.get(username="sabine")
        user_bailleur = User.objects.get(username="raph")
        self.assertTrue(
            user_superuser.is_administrator(),
        )
        self.assertTrue(
            user_superuser.is_administrator(user_instructeur),
        )
        self.assertTrue(
            user_superuser.is_administrator(user_bailleur),
        )
        self.assertFalse(
            user_instructeur.is_administrator(),
        )
        self.assertFalse(
            user_bailleur.is_administrator(),
        )
        user_instructeur.administrateur_de_compte = True
        self.assertTrue(
            user_instructeur.is_administrator(),
        )
        self.assertFalse(
            user_instructeur.is_administrator(user_superuser),
            "un administrateur de compte ne peut pas être administrateur d'un super utilisateur",
        )
        user_instructeur_metropole = User.objects.get(username="roger")
        self.assertTrue(
            user_instructeur.is_administrator(user_instructeur_metropole),
            "un administrateur de compte est administrateur des instructeurs"
            + " qui ont au moins une administration en commun",
        )
        user_instructeur_paris = User.objects.get(username="fix")
        self.assertFalse(
            user_instructeur.is_administrator(user_instructeur_paris),
            "un administrateur de compte n'est pas administrateur"
            + " des instructeurs qui n'ont pas au moins une administration en commun",
        )

        user_bailleur.administrateur_de_compte = True
        self.assertTrue(
            user_bailleur.is_administrator(),
        )
        self.assertFalse(
            user_bailleur.is_administrator(user_superuser),
            "un administrateur de compte ne peut pas être administrateur d'un super utilisateur",
        )
        user_bailleur_hlm = User.objects.get(username="sophie")
        self.assertTrue(
            user_bailleur.is_administrator(user_bailleur_hlm),
            "un administrateur de compte est administrateur des bailleurs"
            + " qui ont au moins un bailleur en commun",
        )
        user_bailleur_sem = User.objects.get(username="sylvie")
        self.assertFalse(
            user_bailleur.is_administrator(user_bailleur_sem),
            "un administrateur de compte n'est pas administrateur des bailleurs"
            + " qui n'ont pas au moins un bailleur en commun",
        )

    def test_is_administration_administrator(self):
        user_superuser = User.objects.get(username="nicolas")
        administration_arles = Administration.objects.get(code="12345")
        administration_paris = Administration.objects.get(code="75000")
        user_instructeur = User.objects.get(username="sabine")
        user_bailleur = User.objects.get(username="raph")
        self.assertTrue(
            user_superuser.is_administration_administrator(administration_arles),
        )
        self.assertTrue(
            user_superuser.is_administration_administrator(administration_paris),
        )
        user_instructeur.administrateur_de_compte = True
        self.assertTrue(
            user_instructeur.is_administration_administrator(administration_arles),
            "un administrateur de compte est seulement administrateur des"
            + " administrations qui lui sont liées par un role",
        )
        self.assertFalse(
            user_instructeur.is_administration_administrator(administration_paris),
            "un administrateur de compte est seulement administrateur des"
            + " administrations qui lui sont liées par un role",
        )
        user_instructeur.administrateur_de_compte = False
        self.assertFalse(
            user_instructeur.is_administration_administrator(administration_arles),
            "un non administrateur de compte n'est pas administrateur d'une administration",
        )
        self.assertFalse(
            user_instructeur.is_administration_administrator(administration_paris),
            "un non administrateur de compte n'est pas administrateur d'une administration",
        )
        user_bailleur.administrateur_de_compte = True
        self.assertFalse(
            user_bailleur.is_administration_administrator(administration_arles),
            "un bailleur ne peut pas être administrateur d'une administration",
        )
        self.assertFalse(
            user_bailleur.is_administration_administrator(administration_paris),
            "un bailleur ne peut pas être administrateur d'une administration",
        )
        user_bailleur.administrateur_de_compte = False
        self.assertFalse(
            user_bailleur.is_administration_administrator(administration_arles),
            "un bailleur ne peut pas être administrateur d'une administration",
        )

    def test_is_bailleur_administrator(self):
        user_superuser = User.objects.get(username="nicolas")
        user_instructeur = User.objects.get(username="sabine")
        user_bailleur = User.objects.get(username="raph")
        bailleur_hlm = Bailleur.objects.get(nom="HLM")
        bailleur_sem = Bailleur.objects.get(nom="SEM")
        self.assertTrue(
            user_superuser.is_bailleur_administrator(bailleur_hlm),
            "un superuser est administrateur de tous les bailleurs",
        )
        self.assertTrue(
            user_superuser.is_bailleur_administrator(bailleur_sem),
            "un superuser est administrateur de tous les bailleurs",
        )
        user_bailleur.administrateur_de_compte = True
        self.assertTrue(
            user_bailleur.is_bailleur_administrator(bailleur_hlm),
            "un administrateur de compte est seulement administrateur"
            + " des bailleurs qui lui sont liés par un role",
        )
        self.assertFalse(
            user_bailleur.is_bailleur_administrator(bailleur_sem),
            "un administrateur de compte est seulement administrateur"
            + " des bailleurs qui lui sont liés par un role",
        )
        user_bailleur.administrateur_de_compte = False
        self.assertFalse(
            user_bailleur.is_bailleur_administrator(bailleur_hlm),
            "un non administrateur de compte n'est pas administrateur d'un bailleur",
        )
        self.assertFalse(
            user_bailleur.is_bailleur_administrator(bailleur_sem),
            "un non administrateur de compte n'est pas administrateur d'un bailleur",
        )
        user_instructeur.administrateur_de_compte = True
        self.assertFalse(
            user_instructeur.is_bailleur_administrator(bailleur_hlm),
            "un instructeur ne peut pas être administrateur d'un bailleur",
        )
        self.assertFalse(
            user_instructeur.is_bailleur_administrator(bailleur_sem),
            "un instructeur ne peut pas être administrateur d'un bailleur",
        )
        user_instructeur.administrateur_de_compte = False
        self.assertFalse(
            user_instructeur.is_bailleur_administrator(bailleur_hlm),
            "un instructeur ne peut pas être administrateur d'un bailleur",
        )

    # Test model Role
    def test_object_role_str(self):
        role = User.objects.get(username="sabine").roles.all()[0]
        expected_object_name = f"{role.user} - {role.typologie} - {role.administration}"
        self.assertEqual(str(role), expected_object_name)
