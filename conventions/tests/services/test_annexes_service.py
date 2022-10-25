from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import (
    UploadForm,
)
from conventions.models import Convention
from conventions.services.services_logements import ConventionAnnexesService
from conventions.services import (
    utils,
)
from core.tests import utils_fixtures
from programmes.forms import AnnexeFormSet, LotAnnexeForm
from users.models import User


class ConventionAnnexesServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.convention_annexes_service = ConventionAnnexesService(
            convention=convention, request=request
        )

    def test_get(self):
        self.convention_annexes_service.get()
        self.assertEqual(
            self.convention_annexes_service.return_status, utils.ReturnStatus.ERROR
        )
        self.assertIsInstance(self.convention_annexes_service.form, LotAnnexeForm)
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
                self.convention_annexes_service.form.initial[lot_field],
                getattr(self.convention_annexes_service.convention.lot, lot_field),
            )
        self.assertIsInstance(self.convention_annexes_service.formset, AnnexeFormSet)
        self.assertIsInstance(self.convention_annexes_service.upform, UploadForm)

    def test_save(self):
        # fixme : service to test
        pass
