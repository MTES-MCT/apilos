from conventions.models import Convention
from conventions.services.cadastre import ConventionCadastreService
from conventions.views.convention_form import ConventionView


class ConventionCadastreView(ConventionView):
    target_template: str = "conventions/cadastre.html"
    service_class = ConventionCadastreService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("programme__referencecadastrales")
            .get(uuid=convention_uuid)
        )
