from conventions.services.residence_attribution import (
    ConventionResidenceAttributionService,
)
from conventions.views.convention_form import ConventionView


class ConventionResidenceAttributionView(ConventionView):
    target_template: str = "conventions/residence_attribution.html"
    service_class = ConventionResidenceAttributionService
