from conventions.services.foyer_attribution import (
    ConventionFoyerAttributionService,
)
from conventions.views.convention_form import (
    ConventionView,
    avenant_foyer_attribution_step,
)


class ConventionFoyerAttributionView(ConventionView):
    target_template: str = "conventions/foyer_attribution.html"
    service_class = ConventionFoyerAttributionService


class AvenantFoyerAttributionView(ConventionFoyerAttributionView):
    form_steps = [avenant_foyer_attribution_step]
