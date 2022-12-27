from conventions.models import Convention
from conventions.services.edd import ConventionEDDService
from conventions.views.convention_form import ConventionView


class ConventionEDDView(ConventionView):
    target_template: str = "conventions/edd.html"
    service_class = ConventionEDDService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("lot")
            .prefetch_related("programme__logementedds")
            .get(uuid=convention_uuid)
        )
