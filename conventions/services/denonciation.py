from django.http import HttpRequest

from conventions.forms import ConventionDenonciationForm
from conventions.models import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionDenonciationService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ConventionDenonciationForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionDenonciationForm(
            initial={
                "uuid": self.convention.uuid,
                "date_denonciation": self.convention.date_denonciation,
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.form = ConventionDenonciationForm(self.request.POST)
        if self.form.is_valid():
            self.convention.date_denonciation = self.form.cleaned_data[
                "date_denonciation"
            ]
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS
