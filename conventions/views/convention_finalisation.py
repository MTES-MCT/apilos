from django import forms
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView

from conventions.models.convention import Convention
from conventions.services import utils
from core.stepper import Stepper


class FinalisationFormBase(forms.Form):
    pass


class FinalisationNumeroForm(FinalisationFormBase):
    uuid = forms.UUIDField(
        required=False,
        label="Finalisation numéro",
    )
    numero = forms.CharField(
        label="Numéro de convention",
        help_text="Cet identifiant proposé est unique et standardisé à l'échelle nationale."
        '<a href="https://siap-logement.atlassian.net/wiki/x/f4Bu">En savoir plus</a>',
        max_length=255,
        min_length=1,
        required=True,
        error_messages={
            "required": "Le numéro de la convention est obligatoire",
            "min_length": "Le numéro de la convention est obligatoire",
            "max_length": "Le numéro de la convention ne doit pas excéder 255 caractères",
        },
    )


class FinalisationCerfaForm(FinalisationFormBase):
    uuid = forms.UUIDField(
        required=False,
        label="Finalisation cerfa",
    )
    fichier_override_cerfa = forms.CharField(required=False, label="Cerfa personalisé")
    fichier_override_cerfa_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type docx sont acceptés dans la limite de 100 Mo",
    )


class FinalisationServiceBase:
    form: FinalisationFormBase
    convention: Convention

    def __init__(self, convention_uuid: str, request: HttpRequest) -> None:
        self.convention = Convention.objects.get(uuid=convention_uuid)
        if request.method == "POST":
            self.form = FinalisationNumeroForm(request.POST, request.FILES)
        else:
            self.form = FinalisationNumeroForm(
                initial={"numero": self.convention.numero}
            )


class FinalisationNumeroService(FinalisationServiceBase):
    form: FinalisationNumeroForm

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


class FinalisationBase(TemplateView):
    service_class: FinalisationServiceBase

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stepper = Stepper(
            steps=[
                "Valider le numéro de la convention",
                "Vérifier le document CERFA",
                "Valider et envoyer la convention pour signature",
            ]
        )

    def get_context_data(self, **kwargs):
        convention_uuid = str(kwargs.get("convention_uuid"))
        service = self.service_class(
            convention_uuid=convention_uuid, request=self.request
        )

        context = super().get_context_data(**kwargs)
        context["convention"] = service.convention
        context["form_step"] = self.stepper.get_form_step(step_number=self.step_number)
        context["form"] = service.form
        return context


class FinalisationNumero(FinalisationBase):
    template_name = "conventions/finalisation/numero.html"
    step_number = 1
    service_class = FinalisationNumeroService

    def post(self, request, **kwargs):
        convention_uuid = str(kwargs.get("convention_uuid"))
        service = self.service_class(convention_uuid=convention_uuid, request=request)

        if service.save() == utils.ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse(
                    "conventions:finalisation_cerfa",
                    kwargs={"convention_uuid": convention_uuid},
                )
            )

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)


class FinalisationCerfa(FinalisationBase):
    template_name = "conventions/finalisation/cerfa.html"
    step_number = 2
    service_class = FinalisationCerfaService

    def post(self, request, **kwargs):
        convention_uuid = str(kwargs.get("convention_uuid"))
        service = self.service_class(convention_uuid=convention_uuid, request=request)

        if service.save() == utils.ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse(
                    "conventions:finalisation_validation",
                    kwargs={"convention_uuid": convention_uuid},
                )
            )

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)


class FinalisationValidation(FinalisationBase):
    template_name = "conventions/finalisation/validation.html"
    step_number = 3
    service_class = FinalisationValidationService
