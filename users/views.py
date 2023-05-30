from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET


def home(request):
    """
    Default access to APiLos Application.
    The user will be redirected following :
      * user is authenticated
      * Application configuration -> redirect to CERBERE if CERBERE is active
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("conventions:index"))
    if request.get_host() in settings.SIAP_DOMAINS:
        return HttpResponseRedirect(reverse("cas_ng_login"))
    # test si authentifié, si oui, rediriger vers convention/index...
    return render(request, "index.html")


@login_required
@require_GET
def search_bailleur(request):
    query = request.GET.get("q", "")

    return JsonResponse(
        [
            {
                "label": b.nom,
                "value": b.uuid,
            }
            for b in request.user.bailleurs(full_scope=True).filter(
                nom__icontains=query
            )[: settings.APILOS_MAX_DROPDOWN_COUNT]
        ],
        safe=False,
    )


@login_required
@require_GET
def search_parent_bailleur(request, bailleur_uuid: str):
    query = request.GET.get("q", "")

    return JsonResponse(
        [
            {
                "label": b.nom,
                "value": b.uuid,
            }
            for b in request.user.bailleurs(full_scope=True)
            .exclude(uuid=bailleur_uuid)
            .filter(parent_id__isnull=True)
            .filter(nom__icontains=query)[: settings.APILOS_MAX_DROPDOWN_COUNT]
        ],
        safe=False,
    )


@login_required
@require_GET
def search_administration(request):
    query = request.GET.get("q", "")

    return JsonResponse(
        [
            {
                "label": a.nom,
                "value": a.uuid,
            }
            for a in request.user.administrations().filter(nom__icontains=query)[
                : settings.APILOS_MAX_DROPDOWN_COUNT
            ]
        ],
        safe=False,
    )
