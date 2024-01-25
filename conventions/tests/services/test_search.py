from django.db import connection
from django.test import TestCase
from unittest_parametrize import ParametrizedTestCase, parametrize

from conventions.models import Convention, ConventionStatut
from conventions.services.search import (
    UserConventionActivesSearchService,
    UserConventionEnInstructionSearchService,
    UserConventionTermineesSearchService,
)
from conventions.tests.factories import ConventionFactory
from users.tests.factories import UserFactory


class SearchServiceTestBase(ParametrizedTestCase, TestCase):
    __test__ = False

    service_class: type

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    def setUp(self) -> None:
        self.user = UserFactory(is_staff=True, is_superuser=True)
        ConventionFactory(
            lot__programme__ville="Bourg-en-Bresse",
            lot__programme__nom="Le Clos de l'Ille - Rue de l'Occitanie - Séniors",
        )

    def test_no_results(self):
        service = self.service_class(user=self.user, search_filters={"commune": "foo"})
        self.assertEqual(service.get_queryset().count(), 0)

    @parametrize(
        "input, expected_count",
        [
            ("Paris", 0),
            ("Bourg-en-Bresse", 1),
            ("Bourg en Bresse", 1),
            ("bourg en bresse", 1),
            ("bourg en bress", 1),
            ("bourg bresse", 1),
            ("bourg", 1),
            ("bourg en brèsse", 1),
        ],
    )
    def test_search_programme_ville(self, input: str, expected_count: int):
        service = self.service_class(user=self.user, search_filters={"commune": input})
        self.assertEqual(service.get_queryset().count(), expected_count)

    @parametrize(
        "input, expected_count",
        [
            ("Le Clos de l'Ill", 1),
            ("le clos de l'ile", 1),
            ("Occitanie Senior", 1),
        ],
    )
    def test_search_programme_nom(self, input: str, expected_count: int):
        service = self.service_class(
            user=self.user, search_filters={"search_input": input}
        )
        self.assertEqual(service.get_queryset().count(), expected_count)


class TestUserConventionEnInstructionSearchService(SearchServiceTestBase):
    __test__ = True

    service_class = UserConventionEnInstructionSearchService


class TestUserConventionActivesSearchService(SearchServiceTestBase):
    __test__ = True

    service_class = UserConventionActivesSearchService

    def setUp(self) -> None:
        super().setUp()
        Convention.objects.all().update(statut=ConventionStatut.SIGNEE.label)

    def test_search_validation_year(self):
        ConventionFactory(statut=ConventionStatut.SIGNEE.label, valide_le="2023-01-01")
        ConventionFactory(statut=ConventionStatut.SIGNEE.label, valide_le="2020-01-01")

        service = self.service_class(
            user=self.user, search_filters={"validation_year": "2000"}
        )
        self.assertEqual(service.get_queryset().count(), 0)

        service = self.service_class(
            user=self.user, search_filters={"validation_year": "2023"}
        )
        self.assertEqual(service.get_queryset().count(), 1)


class TestUserConventionTermineesSearchService(SearchServiceTestBase):
    __test__ = True

    service_class = UserConventionTermineesSearchService

    def setUp(self) -> None:
        super().setUp()
        Convention.objects.all().update(statut=ConventionStatut.RESILIEE.label)
