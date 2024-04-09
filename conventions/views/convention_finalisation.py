from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from waffle.mixins import WaffleFlagMixin

from conventions.services import utils
from conventions.services.finalisation import (
    FinalisationCerfaService,
    FinalisationNumeroService,
    FinalisationServiceBase,
    FinalisationValidationService,
)
from core.stepper import Stepper


class FinalisationBase(WaffleFlagMixin, TemplateView):
    waffle_flag = settings.FLAG_OVERRIDE_CERFA
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
        if hasattr(service, "form"):
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
