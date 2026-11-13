from io import BytesIO

from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase
from openpyxl import load_workbook
from unittest_parametrize import ParametrizedTestCase, parametrize

from conventions.forms import UploadForm
from conventions.forms.convention_form_edd import LogementEDDForm
from conventions.forms.convention_form_selection import CreateConventionMinForm
from conventions.forms.convention_from_operation import AddConventionForm
from conventions.models import Convention
from conventions.services.edd import ConventionEDDService
from conventions.services.logements import ConventionLogementsService
from conventions.services.upload_objects import handle_uploaded_xlsx
from conventions.services.utils import ReturnStatus
from conventions.tests.fixtures import logement_success_payload
from programmes.models import Financement, LogementEDD
from users.models import User

PALULOS_FINANCEMENTS = [Financement.PALULOS]


class EDDFinancementTests(ParametrizedTestCase, TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        self.convention = Convention.objects.get(numero="0001")
        self.request = HttpRequest()
        self.request.user = User.objects.get(username="fix")

    @parametrize("financement", PALULOS_FINANCEMENTS)
    def test_import_and_save_edd_then_logements(self, financement):
        lot = self.convention.lot
        lot.financement = financement
        lot.nb_logements = 2
        lot.save()
        workbook = load_workbook(settings.BASE_DIR / "static/files/logements_edd.xlsx")
        choices = dict(LogementEDDForm.base_fields["financement"].choices)
        worksheet = workbook[LogementEDD.sheet_name]
        for row, designation in enumerate(("B1", "B2"), 3):
            worksheet.cell(row, 1, choices[financement])
            worksheet.cell(row, 2, designation)
            worksheet.cell(row, 3, str(row - 2))

        worksheet["A5"] = "PLAI"
        worksheet["B5"] = "Autre logement"
        worksheet["C5"] = "3"

        excel = BytesIO()
        workbook.save(excel)
        result = handle_uploaded_xlsx(
            UploadForm(), excel, LogementEDD, None, "logements_edd.xlsx"
        )
        self.assertEqual(result["success"], ReturnStatus.SUCCESS)
        self.assertEqual(result["import_warnings"], [])
        self.assertEqual(result["objects"][0]["financement"], financement)
        self.request.POST = {
            "edd_volumetrique_files": "{}",
            "edd_classique_files": "{}",
            "edd_stationnements_files": "{}",
            "form-TOTAL_FORMS": 3,
            "form-INITIAL_FORMS": 0,
            **{
                f"form-{index}-{key}": value
                for index, obj in enumerate(result["objects"])
                for key, value in obj.items()
            },
        }

        service = ConventionEDDService(self.convention, self.request)
        service.save()
        self.assertEqual(service.return_status, ReturnStatus.SUCCESS)
        logement_edd = self.convention.programme.logementedds.get(designation="B1")
        self.assertEqual(logement_edd.financement, financement)
        logement_edd.full_clean()

        self.request.POST = {
            **{
                key: financement if key.endswith("-financement") else value
                for key, value in logement_success_payload.items()
            },
            "lots-0-uuid": str(lot.uuid),
        }
        logements_service = ConventionLogementsService(self.convention, self.request)
        logements_service.save()
        self.assertEqual(logements_service.return_status, ReturnStatus.SUCCESS)
        self.assertEqual(lot.logements.count(), 2)

    @parametrize("financement", PALULOS_FINANCEMENTS)
    def test_logements_reject_mismatched_financement(self, financement):
        for designation in ("B1", "B2"):
            LogementEDD.objects.create(
                programme=self.convention.programme,
                designation=designation,
                financement=financement,
            )
        lot = self.convention.lot
        lot.nb_logements = 2
        lot.save()
        self.request.POST = {
            **logement_success_payload,
            "lots-0-uuid": str(lot.uuid),
        }
        service = ConventionLogementsService(self.convention, self.request)
        service.save()
        self.assertEqual(service.return_status, ReturnStatus.ERROR)
        self.assertTrue(service.formset.forms[0].has_error("designation"))
        self.assertFalse(lot.logements.exists())

    def test_creation_choices_are_unchanged(self):
        expected = ["PLUS", "PLUS_CD", "PLAI", "PLS", "SANS_FINANCEMENT"]
        for form_class in (CreateConventionMinForm, AddConventionForm):
            self.assertEqual(
                [
                    value
                    for value, label in form_class.base_fields["financement"].choices
                ],
                expected,
            )
