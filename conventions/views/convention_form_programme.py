from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.services_programmes import ConventionProgrammeService
from conventions.views.convention_form import ConventionView, avenant_programme_step


class ConventionProgrammeView(ConventionView):
    target_template: str = "conventions/programme.html"
    service_class = ConventionProgrammeService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention.objects.prefetch_related("programme"),
            # .prefetch_related("lot"),
            uuid=convention_uuid,
        )


class AvenantProgrammeView(ConventionProgrammeView):
    form_steps = [avenant_programme_step]
