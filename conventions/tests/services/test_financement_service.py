import datetime

from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import ConventionFinancementForm, PretFormSet, UploadForm
from conventions.models import Convention, Pret, Preteur
from conventions.services import financement as financement_service
from conventions.services import utils
from programmes.models import Financement, TypeOperation
from programmes.models.choices import NatureLogement
from users.models import User

financement_form = {
    "form-TOTAL_FORMS": 2,
    "form-INITIAL_FORMS": 2,
    "form-0-uuid": "",
    "form-0-numero": "A",
    "form-0-financement": "PLUS",
    "form-0-date_octroi": "2020-01-01",
    "form-0-duree": "50",
    "form-0-montant": "1000000.00",
    "form-0-preteur": "CDCF",
    "form-0-autre": "",
    "form-1-uuid": "",
    "form-1-numero": "A",
    "form-1-financement": "PLUS",
    "form-1-date_octroi": "2020-01-01",
    "form-1-duree": "20",
    "form-1-montant": "200000.00",
    "form-1-preteur": "CDCL",
    "form-1-autre": "",
    "annee_fin_conventionnement": "2093",
    "fond_propre": "",
}


class ConventionFinancementServiceTests(TestCase):
    service_class = financement_service.ConventionFinancementService
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
        self.service = self.service_class(convention=convention, request=request)

        avenant = convention.clone(request.user, convention_origin=convention)
        self.service_avenant = self.service_class(convention=avenant, request=request)

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.formset, PretFormSet)
        self.assertIsInstance(self.service.form, ConventionFinancementForm)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_save_success(self):
        self.service.request.POST = financement_form

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        pret_cdcf = Pret.objects.get(
            lot=self.service.convention.lot, preteur=Preteur.CDCF
        )
        self.assertEqual(pret_cdcf.montant, 1000000.00)
        self.assertEqual(pret_cdcf.duree, 50)
        pret_cdcl = Pret.objects.get(
            lot=self.service.convention.lot, preteur=Preteur.CDCL
        )
        self.assertEqual(pret_cdcl.montant, 200000.00)
        self.assertEqual(pret_cdcl.duree, 20)

    def test_duree_is_needed(self):
        self.service.request.POST = {**financement_form, "form-1-duree": ""}
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        form = self.service.formset.forms[1]
        self.assertTrue(form.has_error("duree"))

    def test_cdc_is_needed_failed(self):
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.NEUF
        programme.save()

        self.service.request.POST = {
            **financement_form,
            "form-0-preteur": Preteur.ETAT,
            "form-1-preteur": Preteur.COMMUNE,
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.formset.non_form_errors())

    def test_cdc_is_needed_success(self):
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.NEUF
        programme.save()
        self.service.request.POST = {
            **financement_form,
            "form-0-preteur": Preteur.CDCF,
            "form-1-preteur": Preteur.COMMUNE,
        }
        self.service.save()
        self.assertFalse(self.service.formset.non_form_errors())

    def test_cdc_isnot_needed_success(self):
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.SANSTRAVAUX
        programme.save()
        self.service.request.POST = {
            **financement_form,
            "form-0-preteur": Preteur.ETAT,
            "form-1-preteur": Preteur.COMMUNE,
        }
        self.service.save()
        self.assertFalse(self.service.formset.non_form_errors())

    def test_year_isnot_too_far(self):
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.NEUF
        programme.save()
        self.service.request.POST = {
            **financement_form,
            "annee_fin_conventionnement": datetime.date.today().year + 501,
        }
        self.service.save()

        form = self.service.form
        self.assertTrue(form.has_error("annee_fin_conventionnement"))

    def test_year_max_limit_disabled(self):
        self.service.convention.lot.financement = Financement.PLS
        self.service.convention.save()
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.NEUF
        programme.nature_logement = NatureLogement.AUTRE
        programme.save()
        self.service.request.POST = {
            **financement_form,
            "annee_fin_conventionnement": datetime.date.today().year + 50,
        }
        self.service.save()

        form = self.service.form
        # Convention is of type foyer, so the max limit for PLS is disabled, no error
        assert form.errors == {}

    def test_outre_mer_sans_travaux_date_fin_conventionnement(self):
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.SANSTRAVAUX
        programme.code_insee_departement = "971"
        programme.save()

        self.service.request.POST = {
            **financement_form,
            "annee_fin_conventionnement": datetime.date.today().year + 8,
        }
        self.service.save()

        form = self.service.form
        self.assertTrue(form.has_error("annee_fin_conventionnement"))

        self.service.request.POST = {
            **financement_form,
            "annee_fin_conventionnement": datetime.date.today().year + 9,
        }
        self.service.save()

        form = self.service.form
        assert form.errors == {}

    def test_outre_mer_lls_date_fin_conventionnement(self):
        self.service.convention.lot.financement = Financement.LLS
        self.service.convention.save()
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.REHABILITATION
        programme.code_insee_departement = "971"
        programme.save()

        self.service.request.POST = {
            **financement_form,
            "annee_fin_conventionnement": 2069,
        }
        self.service.save()

        form = self.service.form
        self.assertTrue(form.has_error("annee_fin_conventionnement"))

        self.service.request.POST = {
            **financement_form,
            "annee_fin_conventionnement": 2070,
        }
        self.service.save()

        form = self.service.form
        assert form.errors == {}

    def test_pls_avenant_date_fin_conventionnement(self):
        for financement in [
            Financement.PLS,
            Financement.PLS_DOM,
            Financement.PALUCOM,
            Financement.PALULOS,
            Financement.PALU_AV_21,
            Financement.PALU_COM,
            Financement.PALU_RE,
        ]:
            self.service_avenant.convention.financement = financement
            self.service_avenant.convention.save()
            lot = self.service_avenant.convention.lot
            lot.financement = financement
            lot.save()

            self.service_avenant.request.POST = {
                **financement_form,
                "annee_fin_conventionnement": 2065,
            }
            self.service_avenant.save()

            form = self.service_avenant.form
            assert form.errors == {}


def test_formset_validate_numero_unicity_fail():
    upload_result = {
        "objects": [
            {"numero": "1"},
            {"numero": "2"},
            {"numero": "1"},
            {"numero": "3"},
            {"numero": "3"},
        ]
    }

    formset = PretFormSet(initial=upload_result["objects"])
    is_valid = formset.validate_initial_numero_unicity()

    assert not is_valid
    assert formset.forms[0].errors == {
        "numero": ["Le numéro de financement 1 n'est pas unique."]
    }
    assert formset.forms[1].errors == {}
    assert formset.forms[3].errors == {
        "numero": ["Le numéro de financement 3 n'est pas unique."]
    }


def test_formset_validate_numero_unicity_success():
    upload_result = {"objects": [{"numero": "1"}, {"numero": "2"}, {"numero": "3"}]}

    formset = PretFormSet(initial=upload_result["objects"])
    is_valid = formset.validate_initial_numero_unicity()

    assert is_valid
    for form in formset:
        assert form.errors == {}
