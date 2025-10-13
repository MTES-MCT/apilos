from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.logements import (
    ConventionLogementsService,
)
from conventions.views.convention_form import (
    ConventionView,
    avenant_annexes_step,
    avenant_logements_step,
)


class ConventionLogementsView(ConventionView):
    target_template: str = "conventions/logements.html"
    service_class = ConventionLogementsService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention,
            # Convention.objects.prefetch_related("lot").prefetch_related(
            #     "lot__logements"
            # ),
            uuid=convention_uuid,
        )


class AvenantLogementsView(ConventionLogementsView):
    form_steps = [avenant_logements_step, avenant_annexes_step]
