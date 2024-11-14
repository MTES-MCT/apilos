from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.logements import ConventionFoyerResidenceLogementsService
from conventions.views.convention_form import (
    ConventionView,
    avenant_collectif_step,
    avenant_foyer_residence_logements_step,
)


class ConventionFoyerResidenceLogementsView(ConventionView):
    target_template: str = "conventions/foyer_residence_logements.html"
    service_class = ConventionFoyerResidenceLogementsService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention,
            # Convention.objects.prefetch_related("lot").prefetch_related(
            #     "lot__logements"
            # ),
            uuid=convention_uuid,
        )


class AvenantFoyerResidenceLogementsView(ConventionFoyerResidenceLogementsView):
    form_steps = [avenant_foyer_residence_logements_step, avenant_collectif_step]
