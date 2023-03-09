from django.http import HttpRequest
from django.test import TestCase

from conventions.models import Convention
from conventions.tests.fixtures import collectif_success_payload
from conventions.services import (
    collectif,
    utils,
)
from programmes.models import NatureLogement
from conventions.forms import LocauxCollectifsFormSet, LotCollectifForm
from users.models import User


class ConventionCollectifServiceTests(TestCase):
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
        # convention is foyer
        convention = Convention.objects.get(numero="0001")
        convention.programme.nature_logement = NatureLogement.AUTRE
        convention.programme.save()
        request.user = User.objects.get(username="fix")
        self.service = collectif.ConventionCollectifService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, LotCollectifForm)
        self.assertIsInstance(self.service.formset, LocauxCollectifsFormSet)
        self.assertEqual(
            self.service.form.initial["uuid"],
            self.service.convention.lot.uuid,
        )

    def test_save_success(self):
        self.service.request.POST = collectif_success_payload
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

    def test_save_failed_needed_fields(self):

        self.service.request.POST = {
            **collectif_success_payload,
            "form-1-type_local": "",
            "form-1-surface_habitable": "",
            "form-1-nombre": "",
        }
        self.service.save()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)

        self.assertFalse(self.service.formset.forms[0].has_error("type_local"))
        self.assertFalse(self.service.formset.forms[0].has_error("surface_habitable"))
        self.assertFalse(self.service.formset.forms[0].has_error("nombre"))
        self.assertTrue(self.service.formset.forms[1].has_error("type_local"))
        self.assertTrue(self.service.formset.forms[1].has_error("surface_habitable"))
        self.assertTrue(self.service.formset.forms[1].has_error("nombre"))
