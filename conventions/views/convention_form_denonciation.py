from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.denonciation import ConventionDenonciationService
from conventions.views.convention_form import ConventionView, avenant_denonciation_step


class DenonciationView(ConventionView):
    target_template: str = "conventions/denonciation.html"
    service_class = ConventionDenonciationService
    form_steps = [avenant_denonciation_step]

    def _get_convention(self, convention_uuid):
        return get_object_or_404(Convention, uuid=convention_uuid)
