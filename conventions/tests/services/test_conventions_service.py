import datetime

from django.http import HttpRequest, QueryDict
from django.test import RequestFactory, TestCase

from conventions.models import Convention
from conventions.services.conventions import ConventionService, convention_post_action
from users.models import User


class ConventionServiceImpl(ConventionService):
    def get(self):
        pass

    def save(self):
        pass


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
        self.user = User.objects.get(username="nicolas")
        self.convention = Convention.objects.get(numero="0001")
        self.avenant = self.convention.clone(
            self.user, convention_origin=self.convention
        )
        self.request.user = self.user

    def test_convention_service_basic(self):
        service = ConventionServiceImpl(self.convention, self.request)
        self.assertEqual(self.convention, service.convention)
        self.assertEqual(self.request, service.request)

    def test_convention_post_action_basic(self):
        self.request.POST = QueryDict()
        result = convention_post_action(self.request, self.convention.uuid)

        self.assertEqual(result["convention"], self.convention)
        self.assertEqual(
            len(result["avenants"].object_list), len(self.convention.avenants.all())
        )
        self.assertEqual(result["total_avenants"], 1)

    def test_convention_post_action_resiliation_date(self):
        request = RequestFactory().post("/", data={"date_resiliation": "2024-03-01"})

        convention_post_action(request, self.convention.uuid)

        self.convention.refresh_from_db()
        assert self.convention.date_resiliation == datetime.date(2024, 3, 1)
