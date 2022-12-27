from conventions.services.commentaires import ConventionCommentsService
from conventions.views.convention_form import ConventionView


class ConventionCommentsView(ConventionView):
    target_template: str = "conventions/comments.html"
    service_class = ConventionCommentsService


class AvenantCommentsView(ConventionCommentsView):
    pass
