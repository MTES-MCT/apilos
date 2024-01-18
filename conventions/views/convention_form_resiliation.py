from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.denonciation import ConventionResiliationService
from conventions.views.convention_form import ConventionView, avenant_resiliation_step


class ResiliationView(ConventionView):
    target_template: str = "conventions/resiliation.html"
    service_class = ConventionResiliationService
    form_steps = [avenant_resiliation_step]

    def _get_convention(self, convention_uuid):
        return get_object_or_404(Convention, uuid=convention_uuid)
