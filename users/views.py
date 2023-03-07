from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET

from bailleurs.models import Bailleur


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

@login_required
@require_GET
def search_bailleur(request):
    query = request.GET.get("q", "")

    if len(query) > 2:
        return JsonResponse(
            [
                {
                    "label": b.nom,
                    "value": b.id,
                }
                for b in request.user.bailleurs().filter(nom__icontains=query)[:20]
            ],
            safe=False,
        )

    return JsonResponse([], safe=False)


@login_required
@require_POST
def update_user_popup(request):
    request.user.read_popup = "True"
    request.user.save()
    is_ecolo = request.POST.get("ecolo", False)
    if is_ecolo:
        return HttpResponseRedirect(reverse("conventions:search_completed"))
    else:
        return redirect(request.META.get("HTTP_REFERER", reverse("conventions:index")))
