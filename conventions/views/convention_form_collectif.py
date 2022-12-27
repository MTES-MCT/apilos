from conventions.models import Convention
from conventions.services.collectif import ConventionCollectifService
from conventions.views.convention_form import ConventionView


class ConventionCollectifView(ConventionView):
    target_template: str = "conventions/collectif.html"
    service_class = ConventionCollectifService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements__annexes")
            .get(uuid=convention_uuid)
        )


class AvenantCollectifView(ConventionCollectifView):
    pass
