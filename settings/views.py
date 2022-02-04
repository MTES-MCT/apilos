from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from settings import services


def index(request):
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse("settings:users"))
    if request.user.is_bailleur():
        return HttpResponseRedirect(reverse("settings:bailleurs"))
    if request.user.is_instructeur():
        return HttpResponseRedirect(reverse("settings:administrations"))
    return HttpResponseRedirect(reverse("settings:users"))


def administrations(request):
    result = services.administration_list(request)
    return render(
        request,
        "settings/administrations.html",
        {**result},
    )


def edit_administration(request, administration_uuid):
    result = services.edit_administration(request, administration_uuid)
    if result["success"]:
        return HttpResponseRedirect(reverse("settings:administrations"))
    return render(
        request,
        "settings/edit_administration.html",
        {**result},
    )


def bailleurs(request):
    result = services.bailleur_list(request)
    return render(
        request,
        "settings/bailleurs.html",
        {**result},
    )


def edit_bailleur(request, bailleur_uuid):
    result = services.edit_bailleur(request, bailleur_uuid)
    if result["success"]:
        return HttpResponseRedirect(reverse("settings:bailleurs"))
    return render(
        request,
        "settings/edit_bailleur.html",
        {**result},
    )


def profile(request):
    result = services.user_profile(request)
    return render(
        request,
        "settings/user_profile.html",
        {**result},
    )


def users(request):
    result = services.user_list(request)
    return render(
        request,
        "settings/users.html",
        {**result},
    )


def edit_user(request, username):
    result = services.edit_user(request, username)
    if result["success"]:
        return HttpResponseRedirect(reverse("settings:users"))
    return render(
        request,
        "settings/edit_user.html",
        {**result},
    )


def add_user_bailleur(request, username):
    result = services.add_user_bailleur(request, username)
    if result["success"]:
        return HttpResponseRedirect(
            reverse("settings:edit_user", args=[result["user"].username])
        )
    return render(
        request,
        "settings/edit_user.html",
        {**result},
    )
