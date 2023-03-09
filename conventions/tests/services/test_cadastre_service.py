from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import UploadForm

from conventions.forms import ProgrammeCadastralForm, ReferenceCadastraleFormSet
from conventions.models import Convention
from conventions.services import cadastre as service_cadatsre, utils
from users.models import User


class ConventionCadastreServiceTests(TestCase):
    service_class = service_cadatsre.ConventionCadastreService
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
        self.assertIsInstance(self.service.formset, ReferenceCadastraleFormSet)
        self.assertIsInstance(self.service.form, ProgrammeCadastralForm)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_save(self):
        self.service.request.POST = {
            "permis_construire": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-section": "",
            "form-0-numero": "13",
            "form-0-lieudit": "Marseille",
            "form-0-surface": "0 ha 1 a 27 ca",
            "form-1-uuid": "",
            "form-1-section": "AC",
            "form-1-numero": "15",
            "form-1-lieudit": "Marseille",
            "form-1-surface": "0 ha 1 a 2 ca",
            "effet_relatif_files": "{}",
            "acte_de_propriete_files": "{}",
            "certificat_adressage_files": "{}",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        form = self.service.formset.forms[0]
        self.assertTrue(form.has_error("section"))

        self.service.request.POST = {
            "permis_construire": "123456789 AB",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-section": "AC",
            "form-0-numero": "13",
            "form-0-lieudit": "Marseille",
            "form-0-surface": "0 ha 1 a 27 ca",
            "form-1-uuid": "",
            "form-1-section": "AC",
            "form-1-numero": "15",
            "form-1-lieudit": "Marseille",
            "form-1-surface": "0 ha 1 a 2 ca",
            "effet_relatif_files": "{}",
            "acte_de_propriete_files": "{}",
            "certificat_adressage_files": "{}",
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        self.assertEqual(
            self.service.convention.programme.permis_construire, "123456789 AB"
        )

        ref_cadastrales = self.service.convention.programme.referencecadastrales.all()

        self.assertEqual(
            {ref_cadastrale.lieudit for ref_cadastrale in ref_cadastrales},
            {"Marseille"},
        )
        self.assertEqual(
            {ref_cadastrale.section for ref_cadastrale in ref_cadastrales},
            {"AC"},
        )
        self.assertEqual(
            {ref_cadastrale.surface for ref_cadastrale in ref_cadastrales},
            {"0 ha 1 a 2 ca", "0 ha 1 a 27 ca"},
        )
        self.assertEqual(
            {ref_cadastrale.numero for ref_cadastrale in ref_cadastrales},
            {13, 15},
        )
