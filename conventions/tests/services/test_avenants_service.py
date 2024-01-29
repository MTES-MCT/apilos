from django.http import HttpRequest
from django.test import TestCase

from conventions.models import Convention, ConventionStatut
from conventions.services.avenants import (  # complete_avenants_for_avenant,
    OngoingAvenantError,
    _get_last_avenant,
    create_avenant,
    upload_avenants_for_avenant,
)
from conventions.services.utils import ReturnStatus
from users.models import User


class DummyRequest:
    method: str
    POST: dict
    user: User

    def __init__(self, method, post, user):
        self.method = method
        if self.method == "POST":
            self.POST = post
        else:
            self.GET = {}
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

    def _create_avenant(self, statut=None):
        request = DummyRequest(
            "POST",
            {"avenant_type": "bailleur"},
            self.user,
        )
        result = create_avenant(request, self.convention.uuid)
        avenant = result["convention"]
        if statut:
            avenant.statut = statut.label
            avenant.save()
        return avenant

    def test_create_avenant_basic(self):
        request = DummyRequest(
            "POST",
            {"avenant_type": "bailleur"},
            self.user,
        )
        result = create_avenant(request, self.convention.uuid)

        self.assertEqual(result["success"], ReturnStatus.SUCCESS)
        self.assertEqual(self.convention.avenants.all().count(), 1)

    def test_create_avenant_without_data(self):
        result = create_avenant(self.request, self.convention.uuid)

        self.assertEqual(result["success"], ReturnStatus.ERROR)
        self.assertEqual(self.convention.avenants.all().count(), 0)

    def test_upload_avenants_for_avenant_basic(self):
        avenant = self._create_avenant()
        request = DummyRequest(
            "GET",
            None,
            self.user,
        )
        result = upload_avenants_for_avenant(request, self.convention.uuid)
        self.assertEqual(result["success"], ReturnStatus.ERROR)
        self.assertIn(avenant, result["avenants"].object_list)

    def test_upload_avenants_for_avenant_with_valid_form(self):
        self._create_avenant()

        # On s'assure que tous les avenants sont finalisés
        Convention.objects.avenants().update(
            statut=ConventionStatut.SIGNEE.label, champ_libre_avenant="Coucou"
        )

        request = DummyRequest(
            "POST",
            {},
            self.user,
        )

        result = upload_avenants_for_avenant(request, self.convention.uuid)
        self.assertEqual(result["success"], ReturnStatus.SUCCESS)
        self.assertEqual(result["convention"].parent_id, self.convention.id)
        self.assertEqual(result["convention"].champ_libre_avenant, "Coucou")
        self.assertNotEqual(self.convention.champ_libre_avenant, "Coucou")

    def test_get_last_avenant_basic(self):
        self._create_avenant(statut=ConventionStatut.SIGNEE)
        last_avenant = self._create_avenant(statut=ConventionStatut.SIGNEE)

        assert _get_last_avenant(self.convention) == last_avenant

    def test_get_last_avenant_ongoing(self):
        request = DummyRequest(
            "POST",
            {"avenant_type": "bailleur"},
            self.user,
        )
        last_avenant = create_avenant(request, self.convention.uuid)["convention"]
        last_avenant.statut = ConventionStatut.PROJET.label
        last_avenant.save()

        with self.assertRaises(OngoingAvenantError) as exc:
            _get_last_avenant(self.convention)
            assert exc.message == "Ongoing avenant already exists"

    def test_get_last_avenant_without_avenants(self):
        self.assertEqual(_get_last_avenant(self.convention), self.convention)
