from siap.siap_client.client import SIAPClient
from core import settings


def get_environment(request):
    data = {}
    data["ENVIRONMENT"] = settings.ENVIRONMENT
    data["CERBERE_AUTH"] = settings.CERBERE_AUTH
    if settings.CERBERE_AUTH:
        client = SIAPClient.get_instance()
        data["RACINE_URL_ACCES_WEB"] = client.racine_url_acces_web
        data["URL_ACCES_WEB"] = client.url_acces_web
        data["URL_ACCES_WEB_OPERATION"] = client.url_acces_web_operation
    return data
