from conventions.services.administration import ConventionAdministrationService
from conventions.views.convention_form import ConventionView


class ConventionAdministrationView(ConventionView):
    target_template: str = "conventions/administration.html"
    redirect_on_success: str = "conventions:search_instruction"
    service_class = ConventionAdministrationService
