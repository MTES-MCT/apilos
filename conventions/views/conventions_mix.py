from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from waffle import switch_is_active

from conventions.forms.convention_mixed_form_initialisation import UUIDListForm
from conventions.models.convention import Convention


class ConventionMix(View):

    def post(self, request):
        if not switch_is_active(settings.SWITCH_CONVENTION_MIXTE_ON):
            return HttpResponseRedirect(reverse("conventions:search"))
        form = UUIDListForm(request.POST)
        if form.is_valid():
            uuids = form.cleaned_data["uuids"]
            action = form.cleaned_data["action"]

            if action == "create":
                _, _, convention_mixte = Convention.objects.group_conventions(uuids)
                return HttpResponseRedirect(
                    reverse(
                        "programmes:operation_conventions",
                        args=[convention_mixte.programme.numero_operation],
                    )
                )
            elif action == "dispatch":
                conventions = Convention.objects.degroup_conventions(uuids)
                return HttpResponseRedirect(
                    reverse(
                        "programmes:operation_conventions",
                        args=[conventions.first().programme.numero_operation],
                    )
                )

        # If form is invalid, redirect to search
        return HttpResponseRedirect(reverse("conventions:search"))
