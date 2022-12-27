from conventions.models import Convention
from conventions.services.services_logements import (
    ConventionFoyerResidenceLogementsService,
)
from conventions.views.convention_form import ConventionView


class ConventionFoyerResidenceLogementsView(ConventionView):
    target_template: str = "conventions/foyer_residence_logements.html"
    service_class = ConventionFoyerResidenceLogementsService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements")
            .get(uuid=convention_uuid)
        )


class AvenantFoyerResidenceLogementsView(ConventionFoyerResidenceLogementsView):
    pass
