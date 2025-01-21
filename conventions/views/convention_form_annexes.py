from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.annexes import ConventionAnnexesService
from conventions.views.convention_form import (
    ConventionView,
    avenant_annexes_step,
    avenant_logements_step,
)


class ConventionAnnexesView(ConventionView):
    target_template: str = "conventions/annexes.html"
    service_class = ConventionAnnexesService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention,
            # Convention.objects.prefetch_related("lot").prefetch_related(
            #     "lot__logements__annexes"
            # ),
            uuid=convention_uuid,
        )


class AvenantAnnexesView(ConventionAnnexesView):
    form_steps = [avenant_logements_step, avenant_annexes_step]
