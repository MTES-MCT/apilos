from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.resiliation import (
    ConventionResiliationActeService,
    ConventionResiliationService,
)
from conventions.views.convention_form import (
    ConventionView,
    avenant_resiliation_acte_step,
    avenant_resiliation_creation_step,
    avenant_resiliation_demande_step,
)


class ResiliationCreationView(ConventionView):
    target_template: str = "conventions/resiliation.html"
    service_class = ConventionResiliationService
    form_steps = [avenant_resiliation_creation_step]

    def _get_convention(self, convention_uuid):
        return get_object_or_404(Convention, uuid=convention_uuid)


class ResiliationActeView(ConventionView):
    target_template: str = "conventions/resiliation_acte.html"
    service_class = ConventionResiliationActeService
    form_steps = [avenant_resiliation_demande_step, avenant_resiliation_acte_step]

    def _get_convention(self, convention_uuid):
        return get_object_or_404(Convention, uuid=convention_uuid)


class ResiliationView(ConventionView):
    target_template: str = "conventions/resiliation.html"
    service_class = ConventionResiliationService
    form_steps = [avenant_resiliation_demande_step, avenant_resiliation_acte_step]

    def _get_convention(self, convention_uuid):
        return get_object_or_404(Convention, uuid=convention_uuid)
