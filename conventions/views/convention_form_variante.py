from conventions.services.variantes import ConventionFoyerVariantesService
from conventions.views.convention_form import ConventionView


class ConventionFoyerVariantesView(ConventionView):
    target_template: str = "conventions/variantes.html"
    service_class = ConventionFoyerVariantesService
