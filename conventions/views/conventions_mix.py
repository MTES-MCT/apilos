import logging

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from conventions.forms.convention_mixed_form_initialisation import UUIDListForm
from conventions.services.conventions_mix import OperationConventionMix

logger = logging.getLogger(__name__)


class ConventionMix(View):

    def post(self, request):
        logger.error("am in ConventionMix post function")
        logger.debug("am in ConventionMix post function")
        form = UUIDListForm(request.POST)
        logger.error(f"UUIDListForm : {form}")
        if form.is_valid():
            uuids = form.cleaned_data["uuids"]
            logger.error(f"cleaned uuids : {uuids}")
            service = OperationConventionMix(request, uuids)
            (programme, lots, convention_mixte) = (
                service.get_or_create_conventions_mixte()
            )
            logger.error(f"convention_mixte created : {convention_mixte}")
            logger.error(f"convention_mixte.uuid : {convention_mixte.uuid}")

            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[convention_mixte.uuid])
            )

        return HttpResponseRedirect(reverse("conventions:search"))
