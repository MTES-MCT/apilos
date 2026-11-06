from conventions.services.projet_social import ProjetSocialService
from conventions.views import ConventionView


class ProjetSocialView(ConventionView):
    target_template = "conventions/projet_social.html"
    service_class = ProjetSocialService
