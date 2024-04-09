from django import forms
from django.http import HttpRequest

from conventions.forms.convention_form_finalisation import (
    FinalisationCerfaForm,
    FinalisationNumeroForm,
)
from conventions.models.convention import Convention
from conventions.services import utils


class FinalisationServiceBase:
    form: forms.Form
    convention: Convention


class FinalisationNumeroService(FinalisationServiceBase):
    form: FinalisationNumeroForm

    def __init__(self, convention_uuid: str, request: HttpRequest) -> None:
        self.convention = Convention.objects.get(uuid=convention_uuid)
        if request.method == "POST":
            self.form = FinalisationNumeroForm(
                request.POST, request.FILES, convention=self.convention
            )
        else:
            self.form = FinalisationNumeroForm(
                initial={"numero": self.convention.numero}, convention=self.convention
            )

    def save(self) -> str:
        if self.form.is_valid():
            self.convention.numero = self.form.cleaned_data["numero"]
            self.convention.save()
            return utils.ReturnStatus.SUCCESS
        return utils.ReturnStatus.ERROR


class FinalisationCerfaService(FinalisationServiceBase):
    form: FinalisationCerfaForm

    def __init__(self, convention_uuid: str, request: HttpRequest) -> None:
        self.convention = Convention.objects.get(uuid=convention_uuid)

        if request.method == "POST":
            self.form = FinalisationCerfaForm(
                {
                    "uuid": self.convention.uuid,
                    **utils.init_text_and_files_from_field(
                        request,
                        self.convention,
                        "fichier_override_cerfa",
                    ),
                }
            )
        else:
            self.form = FinalisationCerfaForm(
                initial={
                    "uuid": self.convention.uuid,
                    **utils.get_text_and_files_from_field(
                        "fichier_override_cerfa",
                        self.convention.fichier_override_cerfa,
                    ),
                }
            )

    def save(self) -> str:
        if self.form.is_valid():
            self.convention.fichier_override_cerfa = utils.set_files_and_text_field(
                self.form.cleaned_data["fichier_override_cerfa_files"],
                self.form.cleaned_data["fichier_override_cerfa"],
            )
            self.convention.save()
            return utils.ReturnStatus.SUCCESS
        return utils.ReturnStatus.ERROR


class FinalisationValidationService(FinalisationServiceBase):
    pass
