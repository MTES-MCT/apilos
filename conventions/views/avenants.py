from uuid import UUID

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.http import HttpRequest, HttpResponse

from conventions.forms import AvenantSearchForm
from conventions.services.avenants import (
    create_avenant,
    upload_avenants_for_avenant,
    complete_avenants_for_avenant,
    remove_avenant_type_from_avenant,
)
from conventions.services.selection import ConventionSelectionService
from conventions.services.utils import ReturnStatus
from django.views.decorators.http import require_http_methods


@login_required
@permission_required("convention.add_convention")
def new_avenant(request: HttpRequest, convention_uuid: UUID) -> HttpResponse:
    result = create_avenant(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        convention = result["convention"]
        target_pathname = None
        if result["avenant_type"].nom == "logements":
            if convention.programme.is_foyer() or convention.programme.is_residence():
                target_pathname = "conventions:avenant_foyer_residence_logements"
            else:
                target_pathname = "conventions:avenant_logements"
        if result["avenant_type"].nom == "bailleur":
            target_pathname = "conventions:avenant_bailleur"
        if result["avenant_type"].nom == "programme":
            target_pathname = "conventions:avenant_programme"
        if result["avenant_type"].nom == "duree":
            target_pathname = "conventions:avenant_financement"
        if result["avenant_type"].nom == "champ_libre":
            target_pathname = "conventions:avenant_champ_libre"
        if result["avenant_type"].nom == "commentaires":
            target_pathname = "conventions:avenant_commentaires"
        if target_pathname:
            return HttpResponseRedirect(
                reverse(target_pathname, args=[result["convention"].uuid])
            )

    return render(
        request,
        "conventions/new_avenant.html",
        {
            **result,
        },
    )


@login_required
@permission_required("convention.add_convention")
def new_avenants_for_avenant(
    request: HttpRequest, convention_uuid: UUID
) -> HttpResponse:
    result = upload_avenants_for_avenant(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse(
                "conventions:form_avenants_for_avenant",
                args=[result["convention"].uuid],
            )
        )
    return render(
        request,
        "conventions/avenant/new_avenants_for_avenant.html",
        {
            **result,
        },
    )


@login_required
def form_avenants_for_avenant(request, convention_uuid):
    result = complete_avenants_for_avenant(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse(
                "conventions:new_avenants_for_avenant",
                args=[result["convention_parent"].uuid],
            )
        )
    return render(
        request,
        "conventions/avenant/form_avenants_for_avenant.html",
        {
            **result,
        },
    )


@login_required
@permission_required("convention.add_convention")
@require_http_methods(["POST"])
def remove_from_avenant(
    request: HttpRequest, convention_uuid: UUID
) -> HttpResponseRedirect:
    avenant_type = request.POST.get("avenant_type")
    if avenant_type:
        remove_avenant_type_from_avenant(
            avenant_type=avenant_type, convention_uuid=convention_uuid
        )
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[convention_uuid])
    )


class SearchForAvenantResultView(LoginRequiredMixin, View):
    def get(self, request):
        is_submitted = request.GET.get("departement", None) is not None
        search_form = (
            AvenantSearchForm(request.GET) if is_submitted else AvenantSearchForm()
        )

        if is_submitted and search_form.is_valid():
            conventions = request.user.conventions().filter(
                parent_id__isnull=True,
                programme__code_postal__startswith=search_form.cleaned_data[
                    "departement"
                ].code_postal,
                valide_le__year=search_form.cleaned_data["annee"],
                numero__endswith=search_form.cleaned_data["numero"],
            )

            service = ConventionSelectionService(request)
            service.get_for_avenant()

            return render(
                request,
                "conventions/avenant/search_for_avenant.html",
                {
                    "conventions": conventions,
                    "form": service.form,
                    "editable": True,
                },
            )

        return render(
            request,
            "conventions/avenant/search_for_avenant.html",
            {"conventions": None, "search_form": search_form},
        )

    def post(self, request):
        service = ConventionSelectionService(request)
        service.post_for_avenant()

        if service.return_status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse(
                    "conventions:recapitulatif",
                    args=[service.avenant.uuid],
                )
            )
        return render(
            request,
            "conventions/avenant/search_for_avenant.html",
            {
                "form": service.form,
                "editable": True,
            },
        )
