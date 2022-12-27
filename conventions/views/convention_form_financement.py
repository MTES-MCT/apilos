from conventions.models import Convention
from conventions.services.financement import ConventionFinancementService
from conventions.views.convention_form import ConventionView


class ConventionFinancementView(ConventionView):
    target_template: str = "conventions/financement.html"
    service_class = ConventionFinancementService

    def _get_convention(self, convention_uuid):
        return Convention.objects.prefetch_related("prets").get(uuid=convention_uuid)


class AvenantFinancementView(ConventionFinancementView):
    pass
