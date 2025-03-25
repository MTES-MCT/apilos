from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.edd import ConventionEDDService
from conventions.views.convention_form import ConventionView, avenant_edd_step


class ConventionEDDView(ConventionView):
    target_template: str = "conventions/edd.html"
    service_class = ConventionEDDService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention.objects.prefetch_related("programme")
            # .prefetch_related("lot")
            .prefetch_related("programme__logementedds"),
            uuid=convention_uuid,
        )


class AvenantEDDView(ConventionEDDView):
    form_steps = [avenant_edd_step]
