from conventions.services.bailleurs import ConventionBailleurService
from conventions.views.convention_form import ConventionView


class ConventionBailleurView(ConventionView):
    target_template: str = "conventions/bailleur.html"
    current_path_redirect: str = "conventions:bailleur"
    service_class = ConventionBailleurService

    def post_action(self):
        if bool(self.request.POST.get("change_bailleur", False)):
            self.service.change_bailleur()
        else:
            self.service.update_bailleur()


class AvenantBailleurView(ConventionBailleurView):
    current_path_redirect: str = "conventions:avenant_bailleur"
