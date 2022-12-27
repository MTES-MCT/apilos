from conventions.forms.commentaires import ConventionCommentForm
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionCommentsService(ConventionService):
    form: ConventionCommentForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionCommentForm(
            initial={
                "uuid": self.convention.uuid,
                "comments": self.convention.comments,
                **utils.get_text_and_files_from_field(
                    "comments", self.convention.comments
                ),
                **utils.get_text_and_files_from_field(
                    "attached", self.convention.attached
                ),
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.form = ConventionCommentForm(self.request.POST)
        if self.form.is_valid():
            self.convention.attached = utils.set_files_and_text_field(
                self.form.cleaned_data["attached_files"],
            )
            self.convention.comments = utils.set_files_and_text_field(
                self.form.cleaned_data["comments_files"],
                self.form.cleaned_data["comments"],
            )
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS
