from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from conventions.templatetags import custom_filters


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
