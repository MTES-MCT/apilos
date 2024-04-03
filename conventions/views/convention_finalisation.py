from django import forms
from django.http import HttpRequest
from django.views.generic.base import TemplateView

from conventions.models.convention import Convention
from core.stepper import Stepper


class FinalisationNumeroForm(forms.Form):
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


class FinalisationNumeroService:
    form: FinalisationNumeroForm

    def __init__(self, request: HttpRequest) -> None:
        if request.method == "POST":
            self.form = FinalisationNumeroForm(request.POST)
        else:
            self.form = FinalisationNumeroForm()


class FinalisationNumero(TemplateView):
    template_name = "conventions/finalisation/numero.html"
    step_number = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stepper = Stepper(
            steps=[
                "Valider le numéro de la convention",
                "Vérifier le document CERFA",
                "Valider et envoyer la convention pour signature",
            ]
        )

    def get_context_data(self, convention_uuid, **kwargs):
        context = super().get_context_data(**kwargs)
        context["convention"] = Convention.objects.get(uuid=convention_uuid)
        context["form_step"] = self.stepper.get_form_step(step_number=self.step_number)
        context["form"] = FinalisationNumeroService(self.request).form
        return context
