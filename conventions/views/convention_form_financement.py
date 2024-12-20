from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.financement import ConventionFinancementService
from conventions.views.convention_form import ConventionView, avenant_financement_step


class ConventionFinancementView(ConventionView):
    target_template: str = "conventions/financement.html"
    service_class = ConventionFinancementService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention,
            # Convention.objects.prefetch_related("lot__prets"),
            uuid=convention_uuid,
        )


class AvenantFinancementView(ConventionFinancementView):
    form_steps = [avenant_financement_step]
