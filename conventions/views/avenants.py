from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from conventions.services.avenants import (
    create_avenant,
    search_result,
    upload_avenants_for_avenant,
    complete_avenants_for_avenant,
)
from conventions.services.selection import ConventionSelectionService
from conventions.services.utils import ReturnStatus


@login_required
@permission_required("convention.add_convention")
def new_avenant(request, convention_uuid):
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
        if result["avenant_type"].nom == "duree":
            target_pathname = "conventions:avenant_financement"
        if result["avenant_type"].nom == "commentaires":
            target_pathname = "conventions:avenant_comments"
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
def new_avenants_for_avenant(request, convention_uuid):
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


class SearchForAvenantResultView(LoginRequiredMixin, View):
    def get(self, request):
        result = search_result(request)
        service = ConventionSelectionService(request)
        service.get_from_zero()
        return render(
            request,
            "conventions/avenant/search_for_avenant_result.html",
            {
                **result,
                "form": service.form,
                "editable": True,
            },
        )

    def post(self, request):
        service = ConventionSelectionService(request)
        service.post_from_zero()

        if service.return_status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse(
                    "conventions:new_avenants_for_avenant",
                    args=[service.convention.uuid],
                )
            )
        return render(
            request,
            "conventions/avenant/search_for_avenant_result.html",
            {
                "form": service.form,
                "editable": True,
            },
        )
