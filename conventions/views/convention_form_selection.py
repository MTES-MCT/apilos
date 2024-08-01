from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from conventions.permissions import currentrole_permission_required_view_function
from conventions.services.selection import ConventionSelectionService
from conventions.services.utils import ReturnStatus


class NewConventionAnruView(LoginRequiredMixin, View):
    @currentrole_permission_required_view_function("convention.add_convention")
    def get(self, request):
        service = ConventionSelectionService(request)
        service.get_create_convention()

        return render(
            request,
            "conventions/new_convention_anru.html",
            {
                "form": service.form,
                "editable": True,
            },
        )

    @currentrole_permission_required_view_function("convention.add_convention")
    def post(self, request):
        service = ConventionSelectionService(request)
        service.post_create_convention()

        if service.return_status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[service.convention.uuid])
            )
        return render(
            request,
            "conventions/new_convention_anru.html",
            {
                "form": service.form,
                "editable": True,
            },
        )
