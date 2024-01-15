from django.test import TestCase

from conventions.services.search import (
    UserConventionEnInstructionSearchService,
)
from programmes.models import Programme
from users.models import User


class SearchServiceTestBase(TestCase):
    __test__ = False

    service_class: type

    fixtures = [
        "auth.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self) -> None:
        self.user = User.objects.get(username="nicolas")

    def test_search_programme_ville(self):
        Programme.objects.filter(pk=1).update(ville="Bourg-en-Bresse")
        for city in [
            "Bourg-en-Bresse",
            "Bourg-en-Bresse 2",
            "bourg en bresse",
            "bour en bress",
            "bourg",
        ]:
            service = self.service_class(
                user=self.user, search_filters={"commune": city}
            )
            self.assertGreater(
                service.get_queryset().count(), 1, msg=f"no match for {city})"
            )

    def test_search_programme_nom(self):
        Programme.objects.filter(pk=1).update(
            nom="Le Clos de l'Ille - Rue de l'Occitanie - Séniors"
        )
        for input in [
            "Le Clos de l'Ille",
            "le clos de l'ile",
            "Occitanie Senior",
        ]:
            service = self.service_class(
                user=self.user, search_filters={"search_input": input}
            )
            self.assertGreater(
                service.get_queryset().count(), 1, msg=f"no match for {input})"
            )


class TestUserConventionEnInstructionSearchService(SearchServiceTestBase):
    __test__ = True

    service_class = UserConventionEnInstructionSearchService


# class TestUserConventionActivesSearchService(SearchServiceTestBase):
#     __test__ = True

#     service_class = UserConventionActivesSearchService


# class TestUserConventionTermineesSearchService(SearchServiceTestBase):
#     __test__ = True

#     service_class = UserConventionTermineesSearchService
