from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from bailleurs.models import Bailleur
from conventions.forms import NewConventionForm
from conventions.models import Convention, ConventionStatut
from conventions.services import selection, utils
from instructeurs.models import Administration
from programmes.models import Financement, NatureLogement, TypeHabitat
from users.models import GroupProfile, User


class ConventionSelectionServiceForInstructeurTests(TestCase):
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
        self.request = RequestFactory().get("/conventions/selection")
        self.request.user = User.objects.get(username="fix")
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.service = selection.ConventionSelectionService(request=self.request)

    def test_get_create_convention(self):
        administration = Administration.objects.get(code="75000")
        self.service.get_create_convention()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, NewConventionForm)
        self.assertEqual(
            self.service.form.declared_fields["administration"].choices,
            [(administration.uuid, str(administration))],
        )

    def test_post_create_convention_failed_form(self):
        self.service.request.POST = {}
        self.service.post_create_convention()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("numero_operation"))
        self.assertTrue(self.service.form.has_error("bailleur"))
        self.assertTrue(self.service.form.has_error("administration"))
        self.assertTrue(self.service.form.has_error("nom"))
        self.assertTrue(self.service.form.has_error("nb_logements"))
        self.assertTrue(self.service.form.has_error("nature_logement"))
        self.assertTrue(self.service.form.has_error("type_habitat"))
        self.assertTrue(self.service.form.has_error("financement"))
        self.assertTrue(self.service.form.has_error("code_postal"))
        self.assertTrue(self.service.form.has_error("ville"))

    def test_post_create_convention_failed_scope(self):
        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="12345")
        self.service.request.POST = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
        }
        self.service.post_create_convention()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("administration"))

    def test_post_create_convention_success(self):
        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.service.request.POST = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "numero_operation": "123456789",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
        }
        self.service.post_create_convention()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        self.assertEqual(
            self.service.convention,
            Convention.objects.get(
                programme__nom="Programme de test", lots__financement=Financement.PLUS
            ),
        )
        self.assertEqual(
            self.service.convention.programme.numero_operation, "123456789"
        )

    def test_post_for_avenant_success(self):
        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.service.request.POST = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "financement": Financement.PLAI,
            "code_postal": "20000",
            "ville": "Bisouville",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "nb_logements": "10",
            "statut": ConventionStatut.SIGNEE.label,
            "numero": "2022-75-Rivoli-02-213",
            "numero_avenant": "1",
        }
        self.service.post_for_avenant()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        self.assertEqual(
            self.service.convention,
            Convention.objects.get(
                programme__nom="Programme de test",
                lots__financement=Financement.PLAI,
                parent_id__isnull=True,
            ),
        )


class ConventionSelectionServiceForBailleurTests(TestCase):
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
        self.request = RequestFactory().get("/conventions/selection")
        self.request.user = User.objects.get(username="raph")
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.service = selection.ConventionSelectionService(request=self.request)

    def test_get_create_convention(self):
        administrations = Administration.objects.all().order_by("nom")
        bailleurs = Bailleur.objects.filter(
            siret__in=["987654321", "12345678901234"]
        ).order_by("nom")
        self.service.get_create_convention()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, NewConventionForm)
        self.assertEqual(
            self.service.form.declared_fields["administration"].choices,
            [
                (administration.uuid, str(administration))
                for administration in administrations
            ],
        )
        self.assertEqual(
            self.service.form.declared_fields["bailleur"].queryset.count(),
            bailleurs.count(),
        )

    def test_post_create_convention_failed_form(self):
        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.service.request.POST = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "",
        }
        self.service.post_create_convention()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("ville"))

    def test_post_create_convention_failed_scope(self):
        bailleur = Bailleur.objects.get(siret="2345678901")
        administration = Administration.objects.get(code="75000")
        self.service.request.POST = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
        }
        self.service.post_create_convention()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("bailleur"))

    def test_post_create_convention_success(self):
        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.service.request.POST = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "numero_operation": "123456789",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
        }
        self.service.post_create_convention()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        self.assertEqual(
            self.service.convention,
            Convention.objects.get(
                programme__nom="Programme de test", lots__financement=Financement.PLUS
            ),
        )
        self.assertEqual(
            self.service.convention.programme.nature_logement,
            NatureLogement.LOGEMENTSORDINAIRES,
        )

    def test_post_for_avenant_success(self):
        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.service.request.POST = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "nb_logements": "10",
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
            "statut": ConventionStatut.SIGNEE.label,
            "numero": "2022-75-Rivoli-02-213",
            "numero_avenant": "1",
        }
        self.service.post_for_avenant()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        self.assertEqual(
            self.service.convention,
            Convention.objects.get(
                programme__nom="Programme de test",
                lots__financement=Financement.PLUS,
                parent_id__isnull=True,
            ),
        )
        self.assertEqual(
            self.service.convention.programme.nature_logement,
            NatureLogement.LOGEMENTSORDINAIRES,
        )
