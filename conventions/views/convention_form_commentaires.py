from conventions.services.commentaires import ConventionCommentairesService
from conventions.views.convention_form import ConventionView


class ConventionCommentairesView(ConventionView):
    target_template: str = "conventions/commentaires.html"
    service_class = ConventionCommentairesService


class AvenantCommentsView(ConventionCommentairesView):
    pass
