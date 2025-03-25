from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods

from conventions.forms import AvenantSearchForm
from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from conventions.permissions import (
    currentrole_permission_required,
    currentrole_permission_required_view_function,
)
from conventions.services.avenants import (
    OngoingAvenantError,
    complete_avenants_for_avenant,
    create_avenant,
    remove_avenant_type_from_avenant,
    upload_avenants_for_avenant,
)
from conventions.services.selection import ConventionSelectionService
from conventions.services.utils import ReturnStatus

from conventions.models import AvenantType


@login_required
@currentrole_permission_required("convention.add_convention")
def new_avenant(request: HttpRequest, convention_uuid: UUID) -> HttpResponse:
    try:
        result = create_avenant(request, convention_uuid)
    except OngoingAvenantError:
        convention = Convention.objects.get(uuid=convention_uuid)
        last_avenant = (
            convention.avenants.filter(
                statut__in=[
                    ConventionStatut.PROJET.label,
                    ConventionStatut.INSTRUCTION.label,
                    ConventionStatut.CORRECTION.label,
                ]
            )
            .order_by("-cree_le")
            .first()
        )
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[last_avenant.uuid])
        )
    if result["success"] == ReturnStatus.SUCCESS and result["avenant_type"]:
        if target_pathname := _get_path_name_for_avenant_type(
            avenant_type=result["avenant_type"], convention=result["convention"]
        ):
            return HttpResponseRedirect(
                reverse(target_pathname, args=[result["convention"].uuid])
            )

    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


def _get_path_name_for_avenant_type(
    avenant_type: AvenantType, convention: Convention
) -> str | None:
    match avenant_type.nom:
        case "logements":
            if convention.programme.is_foyer or convention.programme.is_residence:
                return "conventions:avenant_foyer_residence_logements"
            return "conventions:avenant_logements"
        case "bailleur":
            return "conventions:avenant_bailleur"
        case "programme":
            return "conventions:avenant_programme"
        case "edd":
            return "conventions:avenant_edd"
        case "duree":
            return "conventions:avenant_financement"
        case "champ_libre":
            return "conventions:avenant_champ_libre"
        case "commentaires":
            return "conventions:avenant_commentaires"
        case _:
            return None


@login_required
@currentrole_permission_required("convention.add_convention")
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


# FIXME : update to View class
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
@currentrole_permission_required("convention.add_convention")
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
    @currentrole_permission_required_view_function("convention.view_convention")
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

    @currentrole_permission_required_view_function("convention.add_convention")
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
