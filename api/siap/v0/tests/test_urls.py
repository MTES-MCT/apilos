import importlib
from contextlib import contextmanager

from django.test import override_settings
from django.urls import NoReverseMatch, clear_url_caches, reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.siap.v0 import urls as siap_v0_urls
from core import urls as core_urls
from siap.siap_client.client import build_jwt
from users.models import User


def _reload_urls():
    importlib.reload(siap_v0_urls)
    importlib.reload(core_urls)
    clear_url_caches()


@contextmanager
def reload_urlconf_with_debug(debug: bool):
    try:
        with override_settings(DEBUG=debug):
            _reload_urls()
            yield
    finally:
        _reload_urls()


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class SiapApiDocUrlsTest(APITestCase):
    def setUp(self):
        user = User.objects.create_superuser(
            "super.user", "super.user@apilos.com", "12345"
        )
        user.cerbere_login = "my.name@beta.gouv.fr"
        user.save()

    def test_doc_and_debug_routes_are_disabled_when_debug_is_false(self):
        with reload_urlconf_with_debug(False):
            for path in (
                "/api-siap/v0/schema/",
                "/api-siap/v0/schema-ui/",
                "/api-siap/v0/schema-redoc/",
                "/api-siap/v0/dummy/",
                "/api-siap/v0/api-auth/login/",
            ):
                response = self.client.get(path)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND,
                    f"Expected 404 for {path} when DEBUG=False",
                )

            for url_name in (
                "api-siap:schema",
                "api-siap:schema-ui",
                "api-siap:schema-redoc",
            ):
                with self.assertRaises(NoReverseMatch):
                    reverse(url_name)

            # Runtime SIAP routes remain available
            self.assertEqual(
                self.client.get("/api-siap/v0/config/").status_code,
                status.HTTP_401_UNAUTHORIZED,
            )
            client = APIClient()
            client.credentials(
                HTTP_AUTHORIZATION="Bearer " + build_jwt(user_login="toto")
            )
            self.assertEqual(
                client.get("/api-siap/v0/config/").status_code,
                status.HTTP_200_OK,
            )

    def test_doc_routes_are_enabled_when_debug_is_true(self):
        with reload_urlconf_with_debug(True):
            schema_response = self.client.get("/api-siap/v0/schema/")
            self.assertEqual(schema_response.status_code, status.HTTP_200_OK)
            self.assertIn(b"API APiLos", schema_response.content)

            swagger_response = self.client.get("/api-siap/v0/schema-ui/")
            self.assertEqual(swagger_response.status_code, status.HTTP_200_OK)

            swagger_script_response = self.client.get("/api-siap/v0/schema-ui/?script=")
            self.assertEqual(swagger_script_response.status_code, status.HTTP_200_OK)

            redoc_response = self.client.get("/api-siap/v0/schema-redoc/")
            self.assertEqual(redoc_response.status_code, status.HTTP_200_OK)

            self.assertEqual(
                self.client.get("/api-siap/v0/config/").status_code,
                status.HTTP_401_UNAUTHORIZED,
            )
