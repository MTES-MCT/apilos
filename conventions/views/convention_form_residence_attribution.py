from conventions.services.residence_attribution import (
    ConventionResidenceAttributionService,
)
from conventions.views.convention_form import (
    ConventionView,
    avenant_residence_attribution_step,
)


class ConventionResidenceAttributionView(ConventionView):
    target_template: str = "conventions/residence_attribution.html"
    service_class = ConventionResidenceAttributionService


class AvenantResidenceAttributionView(ConventionResidenceAttributionView):
    form_steps = [avenant_residence_attribution_step]
