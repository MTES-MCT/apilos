from django.http import HttpRequest
from conventions.forms.convention_form_administration import (
    UpdateConventionAdministrationForm,
)

from conventions.models import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionAdministrationService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: UpdateConventionAdministrationForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False

    def get(self):
        self.form = UpdateConventionAdministrationForm(
            user=self.request.user,
            initial={"administration": self.convention.programme.administration},
        )

    def _update_administration(self):
        if self.form.is_valid():
            administration = self.form.cleaned_data["administration"]

            self.convention.programme.administration = administration
            self.convention.programme.save()
            self.return_status = utils.ReturnStatus.REFRESH
