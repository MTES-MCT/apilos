from django.http import HttpRequest
from django.test import TestCase

from conventions.models import Convention, ConventionStatut
from conventions.services.avenants import (
    _get_last_avenant,
    create_avenant,
    # complete_avenants_for_avenant,
    # upload_avenants_for_avenant,
)
from conventions.services.utils import ReturnStatus
from users.models import User


class DummyRequest:
    method: str
    POST: dict
    user: User

    def __init__(self, method, POST, user):
        self.method = method
        self.POST = POST
        self.user = user


class ConventionAvenantsServiceTests(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        self.request = HttpRequest()
        self.convention = Convention.objects.get(numero="0001")
        self.user = User.objects.get(username="nicolas")
        self.request.user = self.user

    def test_create_avenant_basic(self):
        request = DummyRequest(
            "POST",
            {"uuid": self.convention.uuid, "avenant_type": "bailleur"},
            self.user,
        )
        result = create_avenant(request, self.convention.uuid)

        self.assertEqual(result["success"], ReturnStatus.SUCCESS)
        self.assertEqual(self.convention.avenants.all().count(), 0)

    def test_create_avenant_without_data(self):
        result = create_avenant(self.request, self.convention.uuid)

        self.assertEqual(result["success"], ReturnStatus.ERROR)
        self.assertEqual(self.convention.avenants.all().count(), 0)

    def test_upload_avenants_for_avenant_basic(self):
        pass

    def _get_last_avenant_basic(self):
        request = DummyRequest(
            "POST",
            {"uuid": self.convention.uuid, "avenant_type": "bailleur"},
            self.user,
        )

        create_avenant(request, self.convention.uuid)
        last_avenant = create_avenant(request, self.convention.uuid)["convention"]

        self.assertEqual(_get_last_avenant(self.convention), last_avenant)

    def _get_last_avenant_ongoing(self):
        request = DummyRequest(
            "POST",
            {"uuid": self.convention.uuid, "avenant_type": "bailleur"},
            self.user,
        )

        last_avenant = create_avenant(request, self.convention.uuid)["convention"]
        last_avenant.statut = ConventionStatut.PROJET.label
        last_avenant.save()

        with self.assertRaises(Exception):
            _get_last_avenant(self.convention)

    def _get_last_avenant_without_avenants(self):
        self.assertEqual(_get_last_avenant(self.convention), self.convention)
