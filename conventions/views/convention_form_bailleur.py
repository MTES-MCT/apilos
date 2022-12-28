from conventions.services.bailleurs import ConventionBailleurService
from conventions.views.convention_form import ConventionView


class ConventionBailleurView(ConventionView):
    target_template: str = "conventions/bailleur.html"
    current_path_redirect: str = "conventions:bailleur"
    service_class = ConventionBailleurService


class AvenantBailleurView(ConventionBailleurView):
    current_path_redirect: str = "conventions:avenant_bailleur"
