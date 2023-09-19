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
                "date_denonciation": utils.format_date_for_form(
                    self.convention.date_denonciation
                ),
                "motif_denonciation": self.convention.motif_denonciation,
                **utils.get_text_and_files_from_field(
                    "fichier_denonciation", self.convention.fichier_denonciation
                ),
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        initial = {
            "date_denonciation": utils.format_date_for_form(
                self.convention.date_denonciation
            ),
        }
        self.form = ConventionDenonciationForm(self.request.POST, initial=initial)
        if self.form.is_valid():
            self.convention.date_denonciation = self.form.cleaned_data[
                "date_denonciation"
            ]
            self.convention.motif_denonciation = self.form.cleaned_data[
                "motif_denonciation"
            ]
            self.convention.fichier_denonciation = utils.set_files_and_text_field(
                self.form.cleaned_data["fichier_denonciation_files"],
                self.form.cleaned_data["fichier_denonciation"],
            )
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS
