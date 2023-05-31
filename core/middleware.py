from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class ApilosMultisiteMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        if request.get_host() in settings.SIAP_DOMAINS:
            # Configuration du site en version "SIAP"
            request.urlconf = "core.urls.siap"

            if settings.CERBERE_MOCKED:
                settings.AUTHENTICATION_BACKENDS.extend(
                    ["core.backends.MockedCerbereCASBackend"]
                )

                settings.CERBERE_AUTH = request.build_absolute_uri("/cerbere/login")
                settings.CAS_SERVER_URL = settings.CERBERE_AUTH
            else:
                settings.AUTHENTICATION_BACKENDS.extend(
                    ["core.backends.CerbereCASBackend"]
                )
            settings.LOGIN_URL = "/accounts/cerbere-login/"
        else:
            # Configuration du site en version "indépendante"
            request.urlconf = "core.urls.standalone"

            settings.LOGIN_URL = "/accounts/login/"
