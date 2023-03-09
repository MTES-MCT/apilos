from django.http import HttpRequest
from django.test import TestCase
from django.core.exceptions import ValidationError

from conventions.forms import UploadForm, ProgrammeEDDForm, LogementEDDFormSet

from conventions.models import Convention
from conventions.services import (
    edd as service_edd,
    utils,
)
from programmes.models import Financement
from users.models import User


class ConventionEDDServiceTests(TestCase):
    service_class = service_edd.ConventionEDDService
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
        self.assertIsInstance(self.service.formset, LogementEDDFormSet)
        self.assertIsInstance(self.service.form, ProgrammeEDDForm)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_save(self):
        self.service.request.POST = {
            "edd_volumetrique": "",
            "edd_volumetrique_files": "{}",
            "mention_publication_edd_volumetrique": "",
            "edd_classique": "",
            "edd_classique_files": "{}",
            "mention_publication_edd_classique": "",
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 1,
            "form-0-uuid": "",
            "form-0-designation": "A",
            "form-0-numero_lot": "1",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        form = self.service.formset.forms[0]
        self.assertTrue(form.has_error("financement"))

        self.service.request.POST = {
            "edd_volumetrique": "",
            "edd_volumetrique_files": "{}",
            "mention_publication_edd_volumetrique": "",
            "edd_classique": "",
            "edd_classique_files": "{}",
            "mention_publication_edd_classique": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-designation": "A",
            "form-0-numero_lot": "1",
            "form-0-financement": "PLUS",
            "form-1-uuid": "",
            "form-1-designation": "B",
            "form-1-numero_lot": "2",
            "form-1-financement": "PLAI",
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        edd_plai = self.service.convention.programme.logementedds.filter(
            financement=Financement.PLAI
        )
        self.assertEqual(len(edd_plai), 1)
        self.assertEqual(edd_plai.first().designation, "B")
        edd_plus = self.service.convention.programme.logementedds.filter(
            financement=Financement.PLUS
        )
        self.assertEqual(len(edd_plus), 1)
        self.assertEqual(edd_plus.first().designation, "A")

    def test_ignore_optional_error(self):
        self.service.request.POST = {
            "edd_volumetrique": "",
            "edd_volumetrique_files": "{}",
            "mention_publication_edd_volumetrique": "",
            "edd_classique": "",
            "edd_classique_files": "{}",
            "mention_publication_edd_classique": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-designation": "A",
            "form-0-numero_lot": "1",
            "form-0-financement": "PLUS",
            "form-1-uuid": "",
            "form-1-designation": "B",
            "form-1-numero_lot": "2",
            "form-1-financement": "PLUS",
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertEqual(len(getattr(self.service.formset, "optional_errors")), 1)
        self.assertTrue(
            isinstance(
                getattr(self.service.formset, "optional_errors")[0], ValidationError
            )
        )

        self.service.request.POST["ignore_optional_errors"] = "1"
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        edd_plai = self.service.convention.programme.logementedds.filter(
            financement=Financement.PLAI
        )
        self.assertEqual(len(edd_plai), 0)
        edd_plus = self.service.convention.programme.logementedds.filter(
            financement=Financement.PLUS
        )
        self.assertEqual(len(edd_plus), 2)
        self.assertEqual([e.designation for e in edd_plus], ["A", "B"])
