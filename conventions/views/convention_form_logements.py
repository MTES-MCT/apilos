from conventions.models import Convention
from conventions.services.services_logements import ConventionLogementsService
from conventions.views.convention_form import ConventionView


class ConventionLogementsView(ConventionView):
    target_template: str = "conventions/logements.html"
    service_class = ConventionLogementsService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements")
            .get(uuid=convention_uuid)
        )


class AvenantLogementsView(ConventionLogementsView):
    pass
