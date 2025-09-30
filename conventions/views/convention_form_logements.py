from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.logements import (
    ConventionLogementsService,
    ConventionLogementsServiceAvenant,
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


class ConventionLogementsAvenantView(ConventionView):
    # FIXME: Retain the old logic for avenants for now.
    # This class should be removed once avenants are adapted to the mixed convention workflow.
    target_template: str = "conventions/logements.html"
    service_class = ConventionLogementsServiceAvenant  # default

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention,
            uuid=convention_uuid,
        )


class AvenantLogementsView(ConventionLogementsAvenantView):
    form_steps = [avenant_logements_step, avenant_annexes_step]
