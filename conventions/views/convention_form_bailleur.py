from conventions.services.bailleurs import ConventionBailleurService
from conventions.views.convention_form import ConventionView, avenant_bailleur_step


class ConventionBailleurView(ConventionView):
    target_template: str = "conventions/bailleur.html"
    current_path_redirect: str = "conventions:bailleur"
    service_class = ConventionBailleurService
    service: ConventionBailleurService

    def post_action(self):
        if bool(self.request.POST.get("change_bailleur", False)):
            self.service.change_bailleur()
        elif bool(self.request.POST.get("change_administration")):
            self.service.change_administration()
        else:
            self.service.update_bailleur()


class AvenantBailleurView(ConventionBailleurView):
    current_path_redirect: str = "conventions:avenant_bailleur"
    form_steps = [avenant_bailleur_step]
