from conventions.services.administration import ConventionAdministrationService
from conventions.views.convention_form import ConventionView


class ConventionAdministrationView(ConventionView):
    target_template: str = "conventions/administration.html"
    service_class = ConventionAdministrationService
