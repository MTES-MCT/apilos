from conventions.forms.convention_form_projet_social import ProjetSocialForm
from conventions.models import ProjetSocial
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ProjetSocialService(ConventionService):
    form: ProjetSocialForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self) -> None:
        self.form = ProjetSocialForm(
            self.request.POST or None,
            instance=self._get_projet_social(),
            convention=self.convention
        )

    def save(self) -> None:
        self.form = ProjetSocialForm(
            self.request.POST or None,
            instance=self._get_projet_social(),
            convention=self.convention
        )
        if self.form.is_valid():
            self.form.save()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _get_projet_social(self) -> ProjetSocial:
        try:
            projet_social = self.convention.projet_social
        except ProjetSocial.DoesNotExist:
            projet_social = ProjetSocial(convention=self.convention)
        return projet_social
