from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from conventions.services.selection import ConventionSelectionService
from conventions.services.utils import ReturnStatus


class ConventionSelectionFromDBView(LoginRequiredMixin, View):

    # @permission_required("convention.add_convention")
    def get(self, request):
        # Temporarily forbid staff users to create conventions
        if request.user.is_staff:
            raise PermissionDenied

        service = ConventionSelectionService(request)
        service.get_from_db()

        return render(
            request,
            "conventions/selection_from_db.html",
            {
                "form": service.form,
                "lots": service.lots,
                "editable": True,
            },
        )

    # @permission_required("convention.add_convention")
    def post(self, request):
        service = ConventionSelectionService(request)
        service.post_from_db()

        if service.return_status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[service.convention.uuid])
            )
        return render(
            request,
            "conventions/selection_from_db.html",
            {
                "form": service.form,
                "lots": service.lots,
                "editable": True,
            },
        )


class ConventionSelectionFromZeroView(LoginRequiredMixin, View):

    # @permission_required("convention.add_convention")
    def get(self, request):
        service = ConventionSelectionService(request)
        service.get_from_zero()

        return render(
            request,
            "conventions/selection_from_zero.html",
            {
                "form": service.form,
                "editable": True,
            },
        )

    # @permission_required("convention.add_convention")
    def post(self, request):
        service = ConventionSelectionService(request)
        service.post_from_zero()

        if service.return_status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[service.convention.uuid])
            )
        return render(
            request,
            "conventions/selection_from_zero.html",
            {
                "form": service.form,
                "editable": True,
            },
        )
