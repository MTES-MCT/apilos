from conventions.services.projet_social import ProjetSocialService
from conventions.views.convention_form import ConventionView, avenant_projet_social_step

class ProjetSocialView(ConventionView):
    target_template = "conventions/projet_social.html"
    service_class = ProjetSocialService

class AvenantProjetSocialView(ProjetSocialView):
    form_steps = [avenant_projet_social_step]
