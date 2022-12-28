from conventions.models import Convention
from conventions.services.annexes import ConventionAnnexesService
from conventions.views.convention_form import ConventionView


class ConventionAnnexesView(ConventionView):
    target_template: str = "conventions/annexes.html"
    service_class = ConventionAnnexesService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements__annexes")
            .get(uuid=convention_uuid)
        )


class AvenantAnnexesView(ConventionAnnexesView):
    pass
