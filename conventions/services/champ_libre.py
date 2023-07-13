from django.http import HttpRequest

from conventions.forms import ConventionChampLibreForm
from conventions.models import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionChampLibreService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ConventionChampLibreForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionChampLibreForm(
            initial={
                "uuid": self.convention.uuid,
                "champ_libre_avenant": self.convention.champ_libre_avenant,
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.form = ConventionChampLibreForm(self.request.POST)
        if self.form.is_valid():
            self.convention.champ_libre_avenant = self.form.cleaned_data[
                "champ_libre_avenant"
            ]
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS
