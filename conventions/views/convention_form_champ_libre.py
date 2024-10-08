from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.champ_libre import ConventionChampLibreService
from conventions.views.convention_form import ConventionView, avenant_champ_libre_step


class AvenantChampLibreView(ConventionView):
    target_template: str = "conventions/champ_libre.html"
    service_class = ConventionChampLibreService
    form_steps = [avenant_champ_libre_step]

    def _get_convention(self, convention_uuid):
        return get_object_or_404(Convention, uuid=convention_uuid)
