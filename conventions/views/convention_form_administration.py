from conventions.services.administrations import ConventionAdministrationService
from conventions.views.convention_form import ConventionView


class ConventionAdministrationView(ConventionView):
    current_path_redirect: str = "conventions:recapitulatif"
    service_class = ConventionAdministrationService

    def post_action(self):
        pass
        # self.service.update_administration()
