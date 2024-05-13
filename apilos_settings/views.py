from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods

from apilos_settings import services


@require_GET
@login_required
def administrations(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/administrations.html",
        services.administration_list(request),
    )


@require_http_methods(["GET", "POST"])
@login_required
def edit_administration(request: HttpRequest, administration_uuid: str) -> HttpResponse:
    result = services.edit_administration(request, administration_uuid)
    return render(request, "settings/edit_administration.html", result)


@require_GET
@login_required
def bailleurs(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/bailleurs.html",
        services.bailleur_list(request),
    )


@require_http_methods(["GET", "POST"])
@login_required
def edit_bailleur(request: HttpRequest, bailleur_uuid: str) -> HttpResponse:
    result = services.edit_bailleur(request, bailleur_uuid)
    return render(request, "settings/edit_bailleur.html", result)


@require_http_methods(["GET", "POST"])
@login_required
def profile(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/user_profile.html",
        services.user_profile(request),
    )


@require_GET
@login_required
def users(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/users.html",
        services.user_list(request),
    )
