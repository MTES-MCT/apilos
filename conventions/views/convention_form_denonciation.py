from conventions.models import Convention
from conventions.services.denonciation import ConventionDenonciationService
from conventions.views.convention_form import ConventionView


class DenonciationView(ConventionView):
    target_template: str = "conventions/denonciation.html"
    service_class = ConventionDenonciationService

    def _get_convention(self, convention_uuid):
        return Convention.objects.get(uuid=convention_uuid)
