from conventions.models import Convention
from conventions.services.logements import ConventionFoyerResidenceLogementsService
from conventions.views.convention_form import (
    ConventionView,
    avenant_collectif_step,
    avenant_foyer_residence_logements_step,
)


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
    form_steps = [avenant_foyer_residence_logements_step, avenant_collectif_step]
