from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from conventions.templatetags import custom_filters
from users.models import GroupProfile


class TestGetOrderedFullPathFilter(TestCase):
    def setUp(self):
        get_response = mock.MagicMock()
        self.request = RequestFactory().get("/conventions/en-cours")
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_get_ordered_full_path_without_order_field(self):
        self.assertEqual(
            custom_filters.get_ordered_full_path(self.request, ""),
            "/conventions/en-cours?order_by=&page=1",
        )

    def test_get_ordered_full_path_with_order_field(self):
        self.assertEqual(
            custom_filters.get_ordered_full_path(self.request, "field"),
            "/conventions/en-cours?order_by=field&page=1",
        )

    def test_get_ordered_full_path_with_order_field_and_params(self):
        self.request = RequestFactory().get("/conventions/en-cours?params=1")
        self.assertEqual(
            custom_filters.get_ordered_full_path(self.request, "field"),
            "/conventions/en-cours?params=1&order_by=field&page=1",
        )

    def test_get_ordered_full_path_with_same_order_field(self):
        self.request = RequestFactory().get("/conventions/en-cours?order_by=field")
        self.assertEqual(
            custom_filters.get_ordered_full_path(self.request, "field"),
            "/conventions/en-cours?order_by=-field&page=1",
        )


class TestGetAvailableOrderFieldsFilter(TestCase):
    def setUp(self):
        get_response = mock.MagicMock()
        self.request = RequestFactory().get("/conventions")
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_get_ordered_full_path_with_url_operation_conventions(self):
        self.assertEqual(
            custom_filters.get_available_order_fields(
                self.request, "operation_conventions"
            ),
            {},
        )

    def test_get_ordered_full_path_as_bailleur(self):
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertEqual(
            custom_filters.get_available_order_fields(
                self.request, "search_instruction"
            ),
            {
                "programme__administration__nom": "Instructeur",
                "programme__nom": "Opération",
                "lot__financement": "Financement",
                "programme__ville": "Ville",
                "programme__code_postal": "Code postal",
                "lot__nb_logements": "Nombre de logements",
                "programme__date_achevement_compile": "Livraison",
            },
        )
        self.assertEqual(
            custom_filters.get_available_order_fields(self.request, "other_url_name"),
            {
                "programme__administration__nom": "Instructeur",
                "numero": "Numéro",
                "lot__financement": "Financement",
                "programme__ville": "Ville",
                "programme__code_postal": "Code postal",
                "lot__nb_logements": "Nombre de logements",
                "televersement_convention_signee_le": "Signature",
            },
        )

    def test_get_ordered_full_path_as_instructeur(self):
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertEqual(
            custom_filters.get_available_order_fields(
                self.request, "search_instruction"
            ),
            {
                "programme__bailleur__nom": "Bailleur",
                "programme__nom": "Opération",
                "lot__financement": "Financement",
                "programme__code_postal": "Code postal",
                "programme__ville": "Ville",
                "lot__nb_logements": "Nombre de logements",
                "programme__date_achevement_compile": "Livraison",
            },
        )
        self.assertEqual(
            custom_filters.get_available_order_fields(self.request, "other_url_name"),
            {
                "programme__bailleur__nom": "Bailleur",
                "numero": "Numéro",
                "lot__financement": "Financement",
                "programme__ville": "Ville",
                "programme__code_postal": "Code postal",
                "lot__nb_logements": "Nombre de logements",
                "televersement_convention_signee_le": "Signature",
            },
        )


class TestGetOrderValueFilters(TestCase):
    def test_basic(self):
        self.assertEqual(
            custom_filters.get_ordervalue({"param1": "Params"}, "param1"), "Params"
        )

    def test_with_minus(self):
        self.assertEqual(
            custom_filters.get_ordervalue({"param1": "Params"}, "-param1"), "Params"
        )

    def test_noKey(self):
        self.assertEqual(
            custom_filters.get_ordervalue({"param1": "Params"}, "nokey"), ""
        )
