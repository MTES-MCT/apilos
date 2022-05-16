from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings


def home(request):
    """
    Default access to APiLos Application.
    The user will be redirected folowing :
      * user is authenticated
      * Application configuration -> redirect to CERBERE if CERBERE is active
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("conventions:index"))
    if settings.CERBERE_AUTH:
        return HttpResponseRedirect(reverse("cas_ng_login"))
    # test si authentifié, si oui, rediriger vers convention/index...
    return render(request, "index.html")
