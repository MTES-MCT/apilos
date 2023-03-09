from decimal import Decimal
from django.forms import model_to_dict
from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import UploadForm, AnnexeFormSet, LotAnnexeForm
from conventions.models import Convention
from conventions.services.annexes import ConventionAnnexesService
from conventions.services import (
    utils,
)
from programmes.models import Annexe, Logement, TypologieAnnexe, TypologieLogement
from users.models import User

post_fixture = {
    "form-TOTAL_FORMS": "2",
    "form-INITIAL_FORMS": "2",
    "form-0-uuid": "",
    "form-0-typologie": "TERRASSE",
    "form-0-logement_designation": "B1",
    "form-0-logement_typologie": "T1",
    "form-0-surface_hors_surface_retenue": "5.00",
    "form-0-loyer_par_metre_carre": "0.2",
    "form-0-loyer": "1.00",
    "form-1-uuid": "",
    "form-1-typologie": "TERRASSE",
    "form-1-logement_designation": "B2",
    "form-1-logement_typologie": "T1",
    "form-1-surface_hors_surface_retenue": "5.00",
    "form-1-loyer_par_metre_carre": "0.2",
    "form-1-loyer": "1.00",
    "annexe_caves": "FALSE",
    "annexe_soussols": "FALSE",
    "annexe_remises": "FALSE",
    "annexe_ateliers": "FALSE",
    "annexe_sechoirs": "FALSE",
    "annexe_celliers": "FALSE",
    "annexe_resserres": "on",
    "annexe_combles": "on",
    "annexe_balcons": "FALSE",
    "annexe_loggias": "FALSE",
    "annexe_terrasses": "FALSE",
}


class ConventionAnnexesServiceTests(TestCase):
    fixtures = [
        "auth.json",
        # "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.service = ConventionAnnexesService(convention=convention, request=request)
        for designation in ["B1", "B2"]:
            Logement.objects.create(
                designation=designation,
                lot=convention.lot,
                typologie=TypologieLogement.T1,
                surface_habitable=10.00,
                surface_annexes=10.00,
                surface_annexes_retenue=5.00,
                surface_utile=15.00,
                loyer_par_metre_carre=5,
                coeficient=1.0000,
                loyer=75.00,
            )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, LotAnnexeForm)
        for lot_field in [
            "uuid",
            "annexe_caves",
            "annexe_soussols",
            "annexe_remises",
            "annexe_ateliers",
            "annexe_sechoirs",
            "annexe_celliers",
            "annexe_resserres",
            "annexe_combles",
            "annexe_balcons",
            "annexe_loggias",
            "annexe_terrasses",
        ]:
            self.assertEqual(
                self.service.form.initial[lot_field],
                getattr(self.service.convention.lot, lot_field),
            )
        self.assertIsInstance(self.service.formset, AnnexeFormSet)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_save(self):
        self.service.request.POST = {
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        annexes_B1 = Annexe.objects.filter(
            logement__lot=self.service.convention.lot, logement__designation="B1"
        )
        self.assertEqual(annexes_B1.count(), 1)

        self.assertEqual(
            model_to_dict(
                annexes_B1[0],
                fields=[
                    "typologie",
                    "surface_hors_surface_retenue",
                    "loyer_par_metre_carre",
                    "loyer",
                ],
            ),
            {
                "typologie": TypologieAnnexe.TERRASSE,
                "surface_hors_surface_retenue": Decimal("5.00"),
                "loyer_par_metre_carre": Decimal("0.20"),
                "loyer": Decimal("1.00"),
            },
        )
        for annexe in [
            "annexe_caves",
            "annexe_soussols",
            "annexe_remises",
            "annexe_ateliers",
            "annexe_sechoirs",
            "annexe_celliers",
            "annexe_balcons",
            "annexe_loggias",
            "annexe_terrasses",
        ]:
            self.assertFalse(getattr(self.service.convention.lot, annexe))
        for annexe in ["annexe_resserres", "annexe_combles"]:
            self.assertTrue(getattr(self.service.convention.lot, annexe))

    def test_save_ok_on_loyer(self):
        self.service.request.POST = {
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
            "form-1-loyer": "0.01",
        }
        self.service.save()
        self.assertEqual(
            self.service.return_status, utils.ReturnStatus.SUCCESS, "Ok if it is lowers"
        )

        self.service.request.POST = {
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
            "form-1-loyer": "1.1",
        }
        self.service.save()
        self.assertEqual(
            self.service.return_status, utils.ReturnStatus.SUCCESS, "Ok with tolerance"
        )

    def test_save_fails_on_loyer(self):
        self.service.request.POST = {
            "uuid": str(self.service.convention.lot.uuid),
            **post_fixture,
            "form-1-loyer": "1.11",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertFalse(self.service.formset.forms[0].has_error("loyer"))
        self.assertTrue(self.service.formset.forms[1].has_error("loyer"))
