from django.shortcuts import get_object_or_404

from conventions.models import Convention
from conventions.services.cadastre import ConventionCadastreService
from conventions.views.convention_form import ConventionView, avenant_cadastre_step


class ConventionCadastreView(ConventionView):
    target_template: str = "conventions/cadastre.html"
    service_class = ConventionCadastreService

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention.objects.prefetch_related("programme").prefetch_related(
                "programme__referencecadastrales"
            ),
            uuid=convention_uuid,
        )


class AvenantCadastreView(ConventionCadastreView):
    form_steps = [avenant_cadastre_step]
