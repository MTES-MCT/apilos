from conventions.services.attribution import ConventionFoyerAttributionService
from conventions.views.convention_form import ConventionView


class ConventionFoyerAttributionView(ConventionView):
    target_template: str = "conventions/attribution.html"
    service_class = ConventionFoyerAttributionService
