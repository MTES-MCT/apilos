from decimal import Decimal

from django.forms import model_to_dict
from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import AnnexeFormSet, LotAnnexeFormSet, UploadForm
from conventions.models import Convention
from conventions.services import utils
from conventions.services.annexes import ConventionAnnexesService
from programmes.models import Annexe, Logement, TypologieAnnexe, TypologieLogement
from users.models import User

post_fixture = {
    "form-TOTAL_FORMS": "2",
    "form-INITIAL_FORMS": "2",
    "form-0-uuid": "",
    "form-0-typologie": "TERRASSE",
    "form-0-financement": "PLUS",
    "form-0-logement_designation": "B1",
    "form-0-logement_typologie": "T1",
    "form-0-surface_hors_surface_retenue": "5.00",
    "form-0-loyer_par_metre_carre": "0.2",
    "form-0-loyer": "1.00",
    "form-1-uuid": "",
    "form-1-typologie": "TERRASSE",
    "form-1-financement": "PLUS",
    "form-1-logement_designation": "B2",
    "form-1-logement_typologie": "T1",
    "form-1-surface_hors_surface_retenue": "5.00",
    "form-1-loyer_par_metre_carre": "0.2",
    "form-1-loyer": "1.00",
    # LotAnnexeFormSet block
    "lots-TOTAL_FORMS": "1",
    "lots-INITIAL_FORMS": "1",
    "lots-0-uuid": "",
    "lots-0-financement": "PLUS",
    "lots-0-annexe_caves": "FALSE",
    "lots-0-annexe_soussols": "FALSE",
    "lots-0-annexe_remises": "FALSE",
    "lots-0-annexe_ateliers": "FALSE",
    "lots-0-annexe_sechoirs": "FALSE",
    "lots-0-annexe_celliers": "FALSE",
    "lots-0-annexe_resserres": "on",
    "lots-0-annexe_combles": "on",
    "lots-0-annexe_balcons": "FALSE",
    "lots-0-annexe_loggias": "FALSE",
    "lots-0-annexe_terrasses": "FALSE",
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
        self.assertIsInstance(self.service.formset_convention_mixte, LotAnnexeFormSet)
        for form in self.service.formset_convention_mixte:
            for lot_field in [
                "uuid",
                "annexe_caves",
                "financement",
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
                    form.initial[lot_field],
                    getattr(
                        self.service.convention.lots.get(
                            financement=form.initial["financement"]
                        ),
                        lot_field,
                    ),
                )
        self.assertIsInstance(self.service.formset, AnnexeFormSet)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_save(self):
        self.service.request.POST = {
            **post_fixture,
        }

        self.service.save()
        self.service.convention.refresh_from_db()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        annexes_b1 = Annexe.objects.filter(
            logement__lot__in=self.service.convention.lots.all(),
            logement__designation="B1",
        )
        self.assertEqual(annexes_b1.count(), 1)

        self.assertEqual(
            model_to_dict(
                annexes_b1[0],
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
            for lot in self.service.convention.lots.all():
                self.assertFalse(getattr(lot, annexe))
        for annexe in ["annexe_resserres", "annexe_combles"]:
            for lot in self.service.convention.lots.all():
                self.assertTrue(getattr(lot, annexe))

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
