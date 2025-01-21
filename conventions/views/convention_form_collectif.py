from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.collectif import ConventionCollectifService
from conventions.views.convention_form import (
    ConventionView,
    avenant_collectif_step,
    avenant_foyer_residence_logements_step,
)


class ConventionCollectifView(ConventionView):
    target_template: str = "conventions/collectif.html"
    service_class = ConventionCollectifService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention,
            # Convention.objects.prefetch_related("lot").prefetch_related(
            #     "lot__logements__annexes"
            # ),
            uuid=convention_uuid,
        )


class AvenantCollectifView(ConventionCollectifView):
    form_steps = [
        avenant_foyer_residence_logements_step,
        avenant_collectif_step,
    ]
