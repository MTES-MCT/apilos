from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import (
    ConventionFinancementForm,
    PretFormSet,
    UploadForm,
)
from conventions.models import Convention, Pret, Preteur
from conventions.services import (
    financement as financement_service,
    utils,
)
from programmes.models import TypeOperation
from users.models import User


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

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.formset, PretFormSet)
        self.assertIsInstance(self.service.form, ConventionFinancementForm)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_save(self):
        self.service.request.POST = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-numero": "A",
            "form-0-date_octroi": "2020-01-01",
            "form-0-duree": "50",
            "form-0-montant": "1000000.00",
            "form-0-preteur": "CDCF",
            "form-0-autre": "",
            "form-1-uuid": "",
            "form-1-numero": "A",
            "form-1-date_octroi": "2020-01-01",
            "form-1-duree": "",
            "form-1-montant": "200000.00",
            "form-1-preteur": "CDCL",
            "form-1-autre": "",
            "annee_fin_conventionnement": "2093",
            "fond_propre": "",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        form = self.service.formset.forms[1]
        self.assertTrue(form.has_error("duree"))

        self.service.request.POST = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-numero": "A",
            "form-0-date_octroi": "2020-01-01",
            "form-0-duree": "50",
            "form-0-montant": "1000000.00",
            "form-0-preteur": "CDCF",
            "form-0-autre": "",
            "form-1-uuid": "",
            "form-1-numero": "A",
            "form-1-date_octroi": "2020-01-01",
            "form-1-duree": "20",
            "form-1-montant": "200000.00",
            "form-1-preteur": "CDCL",
            "form-1-autre": "",
            "annee_fin_conventionnement": "2093",
            "fond_propre": "",
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        pret_cdcf = Pret.objects.get(
            convention=self.service.convention, preteur=Preteur.CDCF
        )
        self.assertEqual(pret_cdcf.montant, 1000000.00)
        self.assertEqual(pret_cdcf.duree, 50)
        pret_cdcl = Pret.objects.get(
            convention=self.service.convention, preteur=Preteur.CDCL
        )
        self.assertEqual(pret_cdcl.montant, 200000.00)
        self.assertEqual(pret_cdcl.duree, 20)

    def test_cdc_is_needed(self):
        programme = self.service.convention.programme
        programme.type_operation = TypeOperation.NEUF
        programme.save()

        self.service.request.POST = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-numero": "A",
            "form-0-date_octroi": "2020-01-01",
            "form-0-duree": "50",
            "form-0-montant": "1000000.00",
            "form-0-preteur": Preteur.ETAT,
            "form-0-autre": "",
            "form-1-uuid": "",
            "form-1-numero": "A",
            "form-1-date_octroi": "2020-01-01",
            "form-1-duree": "20",
            "form-1-montant": "200000.00",
            "form-1-preteur": Preteur.COMMUNE,
            "form-1-autre": "",
            "annee_fin_conventionnement": "2093",
            "fond_propre": "",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.formset.non_form_errors())

        programme.type_operation = TypeOperation.SANSTRAVAUX
        programme.save()
        self.service.save()
        self.assertFalse(self.service.formset.non_form_errors())

        programme.type_operation = TypeOperation.NEUF
        programme.save()
        self.service.request.POST = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-numero": "A",
            "form-0-date_octroi": "2020-01-01",
            "form-0-duree": "50",
            "form-0-montant": "1000000.00",
            "form-0-preteur": Preteur.CDCF,
            "form-0-autre": "",
            "form-1-uuid": "",
            "form-1-numero": "A",
            "form-1-date_octroi": "2020-01-01",
            "form-1-duree": "20",
            "form-1-montant": "200000.00",
            "form-1-preteur": Preteur.COMMUNE,
            "form-1-autre": "",
            "annee_fin_conventionnement": "2093",
            "fond_propre": "",
        }
        self.service.save()
        self.assertFalse(self.service.formset.non_form_errors())
