from decimal import Decimal
from django.forms import model_to_dict
from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import (
    UploadForm,
)
from conventions.models import Convention
from conventions.services.services_logements import ConventionLogementsService
from conventions.services import (
    utils,
)
from conventions.tests.views.test_logements_view import post_fixture
from core.tests import utils_fixtures
from programmes.forms import LogementFormSet, LotLgtsOptionForm
from programmes.models import Logement
from users.models import User


class ConventionLogementsServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        convention.lot.nb_logements = 2

        request.user = User.objects.get(username="fix")
        self.service = ConventionLogementsService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, LotLgtsOptionForm)
        for lot_field in [
            "uuid",
            "lgts_mixite_sociale_negocies",
            "loyer_derogatoire",
            "nb_logements",
        ]:
            self.assertEqual(
                self.service.form.initial[lot_field],
                getattr(self.service.convention.lot, lot_field),
            )
        self.assertIsInstance(self.service.formset, LogementFormSet)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_save(self):
        self.service.request.POST = {
            "nb_logements": "2",
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        logement_B1 = Logement.objects.prefetch_related("lot").get(
            lot=self.service.convention.lot, designation="B1"
        )

        self.assertEqual(
            model_to_dict(
                logement_B1,
                fields=[
                    "designation",
                    "typologie",
                    "surface_habitable",
                    "surface_annexes",
                    "surface_annexes_retenue",
                    "surface_utile",
                    "loyer_par_metre_carre",
                    "coeficient",
                    "loyer",
                ],
            ),
            {
                "designation": "B1",
                "typologie": "T1",
                "surface_habitable": Decimal("12.12"),
                "surface_annexes": Decimal("45.57"),
                "surface_annexes_retenue": Decimal("0.00"),
                "surface_utile": Decimal("30.00"),
                "loyer_par_metre_carre": Decimal("4.5"),
                "coeficient": Decimal("1.0000"),
                "loyer": Decimal("135.00"),
            },
        )
        self.assertEqual(logement_B1.lot.loyer_derogatoire, 10.00)
        self.assertEqual(logement_B1.lot.lgts_mixite_sociale_negocies, 2)

    def test_save_fails_on_loyer(self):
        self.service.request.POST = {
            "nb_logements": "2",
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
            "form-1-loyer": "750.00",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertFalse(self.service.formset.forms[0].has_error("loyer"))
        self.assertTrue(self.service.formset.forms[1].has_error("loyer"))

    def test_save_fails_on_nb_logements(self):
        self.service.request.POST = {
            "nb_logements": "3",
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
        }
        self.service.save()
        self.assertEqual(
            self.service.formset.non_form_errors(),
            [
                "Le nombre de logement a conventionner (3) ne correspond pas au nombre"
                + " de logements déclaré (2)"
            ],
        )

        self.service.convention.lot.nb_logements = 4
        self.service.convention.lot.save()
        self.service.request.POST = {
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
        }
        self.service.save()
        self.assertEqual(
            self.service.formset.non_form_errors(),
            [
                "Le nombre de logement a conventionner (4) ne correspond pas au nombre"
                + " de logements déclaré (2)"
            ],
        )
