from conventions.services.foyer_attribution import (
    ConventionFoyerAttributionService,
)
from conventions.views.convention_form import ConventionView


class ConventionFoyerAttributionView(ConventionView):
    target_template: str = "conventions/foyer_attribution.html"
    service_class = ConventionFoyerAttributionService
