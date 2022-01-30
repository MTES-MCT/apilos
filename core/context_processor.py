from core import settings


def get_environment(request):
    data = {}
    data["ENVIRONMENT"] = settings.ENVIRONMENT
    data["CERBERE_AUTH"] = settings.CERBERE_AUTH
    return data
