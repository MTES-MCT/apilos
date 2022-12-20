from decimal import Decimal
from django.forms import model_to_dict
from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import (
    UploadForm,
)
from conventions.models import Convention
from conventions.services.services_logements import (
    ConventionFoyerResidenceLogementsService,
)
from conventions.services import (
    utils,
)
from conventions.tests.fixtures import foyer_residence_logement_success_payload

from core.tests import utils_fixtures
from programmes.forms import (
    FoyerResidenceLogementFormSet,
    LotFoyerResidenceLgtsDetailsForm,
)
from programmes.models import Logement, NatureLogement
from users.models import User


class ConventionFoyerResidenceLogementsServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        # convention is foyer
        convention = Convention.objects.get(numero="0001")
        convention.programme.nature_logement = NatureLogement.AUTRE
        convention.programme.save()
        convention.lot.nb_logements = 2
        convention.lot.save()

        request.user = User.objects.get(username="fix")
        self.service = ConventionFoyerResidenceLogementsService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, LotFoyerResidenceLgtsDetailsForm)
        self.assertIsInstance(self.service.formset, FoyerResidenceLogementFormSet)
        self.assertIsInstance(self.service.upform, UploadForm)
        for lot_field in [
            "uuid",
            "surface_habitable_totale",
        ]:
            self.assertEqual(
                self.service.form.initial[lot_field],
                getattr(self.service.convention.lot, lot_field),
            )

    def test_save(self):
        self.service.request.POST = {
            "nb_logements": "2",
            "uuid": str(self.service.convention.lot.uuid),
            **foyer_residence_logement_success_payload,
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        logement_B1 = Logement.objects.prefetch_related("lot").get(
            lot=self.service.convention.lot, designation="b1"
        )

        self.assertEqual(
            model_to_dict(
                logement_B1,
                fields=[
                    "designation",
                    "typologie",
                    "surface_habitable",
                    "loyer",
                ],
            ),
            {
                "designation": "b1",
                "typologie": "T2",
                "surface_habitable": Decimal("16.00"),
                "loyer": Decimal("160.00"),
            },
        )
        self.assertEqual(logement_B1.lot.surface_habitable_totale, 309.00)

    def test_save_fails_on_loyer(self):
        self.service.request.POST = {
            **foyer_residence_logement_success_payload,
            "form-0-typologie": "T2",
            "form-0-loyer": "160.00",
            "form-1-typologie": "T2",
            "form-1-loyer": "161.00",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.formset.non_form_errors())
        self.assertEqual(
            self.service.formset.non_form_errors(),
            [
                "Les loyers doivent-être identiques pour les logements de typologie identique : T2"
            ],
        )

    def test_save_fails_on_nb_logements(self):
        self.service.request.POST = {
            **foyer_residence_logement_success_payload,
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "3",
            "form-2-uuid": "",
            "form-2-designation": "b2",
            "form-2-typologie": "T2",
            "form-2-surface_habitable": "16.00",
            "form-2-loyer": "160.00",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.formset.non_form_errors())
        self.assertEqual(
            self.service.formset.non_form_errors(),
            [
                "Le nombre de logement a conventionner (2) "
                + "ne correspond pas au nombre de logements déclaré (3)"
            ],
        )

    def test_save_fails_on_surface_habitable_totale(self):
        self.service.request.POST = {
            **foyer_residence_logement_success_payload,
            "form-0-surface_habitable": "16.00",
            "form-1-surface_habitable": "16.00",
            "surface_habitable_totale": "31.00",
        }
        self.service.save()
        self.assertTrue(self.service.form.has_error("surface_habitable_totale"))
