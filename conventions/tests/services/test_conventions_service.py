from django.http import HttpRequest, QueryDict
from django.test import TestCase

from conventions.models import Convention
from conventions.services.conventions import ConventionService, convention_sent
from users.models import User


class ConventionConventionsServiceTests(TestCase):
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

    def test_convention_service_basic(self):
        service = ConventionService(self.convention, self.request)

        # Ensure no error is raised when calling these two methods
        service.get()
        service.save()

        self.assertEqual(self.convention, service.convention)
        self.assertEqual(self.request, service.request)

    def test_convention_sent_basic(self):
        result = convention_sent(self.request, self.convention.uuid)
        self.assertEqual(result["convention"], self.convention)

    def test_convention_sent_post(self):
        self.request.method = "POST"
        self.request.POST = QueryDict()
        result = convention_sent(self.request, self.convention.uuid)
        self.assertEqual(result["convention"], self.convention)
