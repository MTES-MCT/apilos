from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.type_stationnement import ConventionTypeStationnementService
from conventions.views.convention_form import ConventionView, avenant_stationnement_step


class ConventionTypeStationnementView(ConventionView):
    target_template: str = "conventions/stationnements.html"
    service_class = ConventionTypeStationnementService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention,
            # Convention.objects.prefetch_related("lot").prefetch_related(
            #     "lot__type_stationnements"
            # ),
            uuid=convention_uuid,
        )


class AvenantTypeStationnementView(ConventionTypeStationnementView):
    form_steps = [avenant_stationnement_step]
