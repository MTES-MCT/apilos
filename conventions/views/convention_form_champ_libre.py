from conventions.models import Convention
from conventions.services.champ_libre import ConventionChampLibreService
from conventions.views.convention_form import ConventionView


class AvenantChampLibreView(ConventionView):
    target_template: str = "conventions/champ_libre.html"
    service_class = ConventionChampLibreService

    def _get_convention(self, convention_uuid):
        return Convention.objects.get(uuid=convention_uuid)
