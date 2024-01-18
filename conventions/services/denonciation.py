from django.http import HttpRequest

from conventions.forms import ConventionDenonciationForm, ConventionResiliationForm
from conventions.models import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionResiliationService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ConventionResiliationForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionResiliationForm(
            initial={
                "uuid": self.convention.uuid,
                "date_resiliation": utils.format_date_for_form(
                    self.convention.date_resiliation
                ),
                "motif_resiliation": self.convention.motif_resiliation,
                "champ_libre_avenant": self.convention.champ_libre_avenant,
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.redirect_recap = bool(self.request.POST.get("redirect_to_recap", False))
        self._resiliation_atomic_update()

    def _resiliation_atomic_update(self):
        self.form = ConventionResiliationForm(
            {
                "uuid": self.convention.uuid,
                **utils.build_partial_form(
                    self.request,
                    self.convention,
                    [
                        "date_resiliation",
                        "motif_resiliation",
                        "champ_libre_avenant",
                    ],
                ),
            }
        )
        if self.form.is_valid():
            self._save_resiliation()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_resiliation(self):
        self.convention.date_resiliation = self.form.cleaned_data["date_resiliation"]
        self.convention.motif_resiliation = self.form.cleaned_data["motif_resiliation"]
        self.convention.champ_libre_avenant = self.form.cleaned_data[
            "champ_libre_avenant"
        ]
        self.convention.save()


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
                    "fichier_instruction_denonciation",
                    self.convention.fichier_instruction_denonciation,
                ),
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.redirect_recap = bool(self.request.POST.get("redirect_to_recap", False))
        self._denonciation_atomic_update()

    def _denonciation_atomic_update(self):
        self.form = ConventionDenonciationForm(
            {
                "uuid": self.convention.uuid,
                **utils.build_partial_form(
                    self.request,
                    self.convention,
                    [
                        "date_denonciation",
                        "motif_denonciation",
                    ],
                ),
                **utils.init_text_and_files_from_field(
                    self.request,
                    self.convention,
                    "fichier_instruction_denonciation",
                ),
            }
        )
        if self.form.is_valid():
            self._save_denonciation()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_denonciation(self):
        self.convention.date_denonciation = self.form.cleaned_data["date_denonciation"]
        self.convention.motif_denonciation = self.form.cleaned_data[
            "motif_denonciation"
        ]
        self.convention.fichier_instruction_denonciation = (
            utils.set_files_and_text_field(
                self.form.cleaned_data["fichier_instruction_denonciation_files"],
                self.form.cleaned_data["fichier_instruction_denonciation"],
            )
        )
        self.convention.save()
