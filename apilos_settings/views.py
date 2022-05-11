from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from apilos_settings import services
from apilos_settings.models import Departement


@login_required
def index(request):
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse("settings:users"))
    if request.user.is_bailleur():
        return HttpResponseRedirect(reverse("settings:bailleurs"))
    if request.user.is_instructeur():
        return HttpResponseRedirect(reverse("settings:administrations"))
    return HttpResponseRedirect(reverse("settings:users"))


@login_required
def administrations(request):
    result = services.administration_list(request)
    return render(
        request,
        "settings/administrations.html",
        {**result},
    )


@login_required
def edit_administration(request, administration_uuid):
    result = services.edit_administration(request, administration_uuid)
    if result["success"]:
        return HttpResponseRedirect(reverse("settings:administrations"))
    return render(
        request,
        "settings/edit_administration.html",
        {**result},
    )


@login_required
def bailleurs(request):
    result = services.bailleur_list(request)
    return render(
        request,
        "settings/bailleurs.html",
        {**result},
    )


@login_required
def edit_bailleur(request, bailleur_uuid):
    result = services.edit_bailleur(request, bailleur_uuid)
    if result["success"]:
        return HttpResponseRedirect(reverse("settings:bailleurs"))
    return render(
        request,
        "settings/edit_bailleur.html",
        {**result},
    )


@login_required
def profile(request):
    result = services.user_profile(request)
    return render(
        request,
        "settings/user_profile.html",
        {
            **result,
            "departements": Departement.objects.all(),
        },
    )


@login_required
def users(request):
    result = services.user_list(request)
    return render(
        request,
        "settings/users.html",
        {**result},
    )


@login_required
def edit_user(request, username):
    result = services.edit_user(request, username)
    if result["status"] == "user_updated":
        return HttpResponseRedirect(reverse("settings:users"))
    if (
        not result["user"].is_instructeur()
        and not result["user"].is_bailleur()
        and not request.user.is_superuser
    ):
        return HttpResponseRedirect(reverse("settings:users"))
    return render(
        request,
        "settings/edit_user.html",
        {
            **result,
            "departements": Departement.objects.all(),
        },
    )


@login_required
def add_user(request):
    result = services.add_user(request)
    if result["status"] == "user_created":
        return HttpResponseRedirect(reverse("settings:users"))
    return render(
        request,
        "settings/add_user.html",
        {
            **result,
            "departements": Departement.objects.all(),
        },
    )


@require_POST
@login_required
@permission_required("users.delete_user")
def delete_user(request, username):
    services.delete_user(request, username)
    return HttpResponseRedirect(reverse("settings:users"))
