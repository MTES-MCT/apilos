from bailleurs.models import NatureBailleur
from conventions.models import ConventionStatut
from core import settings
from siap.siap_client.client import SIAPClient


def get_environment(request):
    data = {}
    data["ENVIRONMENT"] = settings.ENVIRONMENT
    data["SIAP_CLIENT_HOST"] = settings.SIAP_CLIENT_HOST
    data["CERBERE_AUTH"] = settings.CERBERE_AUTH
    data["CONVENTION_STATUT"] = {
        convention_statut.name: convention_statut.label
        for convention_statut in ConventionStatut
    }
    data["NATURE_BAILLEUR"] = {
        nature_bailleur.name: nature_bailleur.label
        for nature_bailleur in NatureBailleur
    }
    data["SIAP_ASSISTANCE_URL"] = settings.SIAP_ASSISTANCE_URL

    if settings.CERBERE_AUTH:
        client = SIAPClient.get_instance()
        data["RACINE_URL_ACCES_WEB"] = client.racine_url_acces_web
        data["URL_ACCES_WEB"] = client.url_acces_web
        data["URL_ACCES_WEB_OPERATION"] = client.url_acces_web_operation
    return data
