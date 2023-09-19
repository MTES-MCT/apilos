from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET


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
    return JsonResponse(
        [
            {
                "label": b.nom + f" ( {b.siren} )" if b.siren else "",
                "value": b.uuid,
            }
            for b in request.user.bailleur_query_set(
                query_string=query, has_no_parent=False
            )
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
                "label": b.nom + f" ( {b.siren} )" if b.siren else "",
                "value": b.uuid,
            }
            for b in request.user.bailleur_query_set(
                query_string=query,
                exclude_bailleur_uuid=bailleur_uuid,
                has_no_parent=True,
            )
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
