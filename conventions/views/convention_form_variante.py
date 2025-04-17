from conventions.services.variantes import ConventionFoyerVariantesService
from conventions.views.convention_form import ConventionView, avenant_variantes_step


class ConventionFoyerVariantesView(ConventionView):
    target_template: str = "conventions/variantes.html"
    service_class = ConventionFoyerVariantesService


class AvenantFoyerVariantesView(ConventionFoyerVariantesView):
    form_steps = [avenant_variantes_step]
