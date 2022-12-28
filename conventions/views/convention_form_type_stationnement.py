from conventions.models import Convention
from conventions.services.type_stationnement import ConventionTypeStationnementService
from conventions.views.convention_form import ConventionView


class ConventionTypeStationnementView(ConventionView):
    target_template: str = "conventions/stationnements.html"
    service_class = ConventionTypeStationnementService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__type_stationnements")
            .get(uuid=convention_uuid)
        )
