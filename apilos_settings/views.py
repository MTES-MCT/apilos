from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_GET

from apilos_settings.services import services_view
from apilos_settings.services import services_view as services
from conventions.services.utils import ReturnStatus


@require_GET
@login_required
def administrations(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/administrations.html",
        services_view.administration_list(request),
    )


@login_required
def edit_administration(request: HttpRequest, administration_uuid: str) -> HttpResponse:
    result = services_view.edit_administration(request, administration_uuid)
    return render(request, "settings/edit_administration.html", result)


@require_GET
@login_required
def bailleurs(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/bailleurs.html",
        services_view.bailleur_list(request),
    )


@login_required
def edit_bailleur(request: HttpRequest, bailleur_uuid: str) -> HttpResponse:
    result = services.edit_bailleur(request, bailleur_uuid)
    return render(request, "settings/edit_bailleur.html", result)


class ImportBailleurUsersView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse("settings:users"))

        service = services.ImportBailleurUsersService(request)
        service.get()
        return render(
            request,
            "settings/import_bailleur_users.html",
            {
                "upform": service.upload_form,
                "formset": service.formset,
            },
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse("settings:users"))

        service = services.ImportBailleurUsersService(request)
        status = service.save()

        if not service.is_upload and status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(reverse("settings:users"))

        return render(
            request,
            "settings/import_bailleur_users.html",
            {
                "upform": service.upload_form,
                "formset": service.formset,
            },
        )


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


@require_GET
@login_required
def edit_user(request: HttpRequest, username: str) -> HttpResponse:
    user_updated, context = services.edit_user(request, username)
    if user_updated:
        return HttpResponseRedirect(reverse("settings:users"))

    if (
        not context["user"].is_instructeur()
        and not context["user"].is_bailleur()
        and not context["user_is_staff_or_admin"]
    ):
        return HttpResponseRedirect(reverse("settings:users"))

    return render(
        request,
        "settings/edit_user.html",
        context,
    )
