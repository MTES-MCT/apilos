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
    numero = forms.CharField(
        label="Numéro de convention",
        help_text="Cet identifiant proposé est unique et standardisé à l'échelle nationale.",
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
    cerfa = forms.FileField()


class FinalisationServiceBase:
    form: FinalisationFormBase
    convention: Convention

    def __init__(self, convention_uuid: str, request: HttpRequest) -> None:
        self.convention = Convention.objects.get(uuid=convention_uuid)
        if request.method == "POST":
            self.form = FinalisationNumeroForm(request.POST, request.FILES)
        else:
            self.form = FinalisationNumeroForm()


class FinalisationNumeroService(FinalisationServiceBase):
    form: FinalisationNumeroForm

    def save(self, numero: str) -> None:
        if self.form.is_valid():
            self.convention.numero = numero
            self.convention.save()
            return utils.ReturnStatus.SUCCESS
        return utils.ReturnStatus.ERROR


class FinalisationCerfaService(FinalisationServiceBase):
    form: FinalisationCerfaForm


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
        numero = kwargs.get("numero")
        convention_uuid = str(kwargs.get("convention_uuid"))
        service = self.service_class(convention_uuid=convention_uuid, request=request)

        if service.save(numero=numero) == utils.ReturnStatus.SUCCESS:
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


class FinalisationValidation(FinalisationBase):
    template_name = "conventions/finalisation/validation.html"
    step_number = 3
    service_class = FinalisationValidationService
