from django.http import HttpRequest

from conventions.forms import (
    ConventionResiliationActeForm,
    ConventionResiliationForm,
)
from conventions.models import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionResiliationActeService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ConventionResiliationActeForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionResiliationActeForm(
            initial={
                "uuid": self.convention.uuid,
                **utils.get_text_and_files_from_field(
                    "fichier_instruction_resiliation",
                    self.convention.fichier_instruction_resiliation,
                ),
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.redirect_recap = bool(self.request.POST.get("redirect_to_recap", False))
        self._resiliation_acte_atomic_update()

    def _resiliation_acte_atomic_update(self):
        self.form = ConventionResiliationActeForm(
            {
                "uuid": self.convention.uuid,
                **utils.init_text_and_files_from_field(
                    self.request,
                    self.convention,
                    "fichier_instruction_resiliation",
                ),
            }
        )
        if self.form.is_valid():
            self._save_resiliation_acte()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_resiliation_acte(self):
        self.convention.fichier_instruction_resiliation = (
            utils.set_files_and_text_field(
                self.form.cleaned_data["fichier_instruction_resiliation_files"],
                self.form.cleaned_data["fichier_instruction_resiliation"],
            )
        )
        self.convention.save()


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
                **utils.get_text_and_files_from_field(
                    "commentaires", self.convention.commentaires
                ),
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
                    ],
                ),
                **utils.init_text_and_files_from_field(
                    self.request,
                    self.convention,
                    "commentaires",
                ),
            }
        )
        if self.form.is_valid():
            self._save_resiliation()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_resiliation(self):
        self.convention.date_resiliation = self.form.cleaned_data["date_resiliation"]
        self.convention.motif_resiliation = self.form.cleaned_data["motif_resiliation"]
        self.convention.commentaires = utils.set_files_and_text_field(
            self.form.cleaned_data["commentaires_files"],
            self.form.cleaned_data["commentaires"],
        )
        self.convention.save()
