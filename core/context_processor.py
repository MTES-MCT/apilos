from django.conf import settings

from conventions.models import ConventionStatut
from siap.siap_client.client import SIAPClient


def get_environment(request):
    data = {}
    data["ENVIRONMENT"] = settings.ENVIRONMENT
    data["SIAP_CLIENT_HOST"] = settings.SIAP_CLIENT_HOST
    data["CRISP_WEBSITE_ID"] = settings.CRISP_WEBSITE_ID
    # Is Mocked Cerbere currently active ?

    data["CONVENTION_STATUT"] = {
        convention_statut.name: convention_statut.label
        for convention_statut in ConventionStatut
    }

    if request.get_host() in settings.SIAP_DOMAINS:
        data["CERBERE_MOCKED"] = settings.CERBERE_MOCKED
        data["CERBERE_AUTH"] = settings.CERBERE_AUTH

        client = SIAPClient.get_instance()
        data["RACINE_URL_ACCES_WEB"] = client.racine_url_acces_web
        data["URL_ACCES_WEB"] = client.url_acces_web
        data["URL_ACCES_WEB_OPERATION"] = client.url_acces_web_operation
    return data
