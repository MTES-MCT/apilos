from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from waffle import switch_is_active

from conventions.forms.convention_mixed_form_initialisation import UUIDListForm
from conventions.models.convention import Convention


class ConventionMix(View):
    """
    View to handle grouping or degrouping of conventions
    based on UUIDs and the requested action ('create' or 'dispatch').
    """

    def post(self, request):
        if not switch_is_active(settings.SWITCH_CONVENTION_MIXTE_ON):
            return HttpResponseRedirect(reverse("conventions:search"))
        form = UUIDListForm(request.POST)
        if form.is_valid():
            uuids = form.cleaned_data.get("uuids", [])
            action = form.cleaned_data.get("action")

            if action == "create":
                _, _, convention_mixte = Convention.objects.group_conventions(uuids)
                return HttpResponseRedirect(
                    reverse(
                        "programmes:operation_conventions",
                        args=[convention_mixte.programme.numero_operation],
                    )
                )
            if action == "dispatch":
                conventions = Convention.objects.degroup_conventions(uuids)
                first_convention = conventions.first()
                if first_convention:
                    return HttpResponseRedirect(
                        reverse(
                            "programmes:operation_conventions",
                            args=[first_convention.programme.numero_operation],
                        )
                    )

        # If form is invalid, redirect to search
        return HttpResponseRedirect(reverse("conventions:search"))
