import json

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView

from conventions.permissions import currentrole_campaign_permission_required
from conventions.services import utils
from conventions.services.finalisation import (
    FinalisationCerfaService,
    FinalisationNumeroService,
    FinalisationServiceBase,
    FinalisationValidationService,
)
from conventions.views.convention_form import BaseConventionView
from core.stepper import Stepper


class FinalisationBase(BaseConventionView, TemplateView):
    service_class: FinalisationServiceBase

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.convention_stepper = Stepper(
            steps=[
                "Valider le numéro de la convention",
                "Vérifier le document CERFA",
                "Valider et envoyer la convention pour signature",
            ]
        )
        self.avenant_stepper = Stepper(
            steps=[
                "Valider le numéro de l'avenant",
                "Vérifier le document CERFA",
                "Valider et envoyer l'avenant pour signature",
            ]
        )

    def get_context_data(self, **kwargs):
        convention_uuid = str(kwargs.get("convention_uuid"))
        service = self.service_class(
            convention_uuid=convention_uuid, request=self.request
        )

        context = super().get_context_data(**kwargs)
        context["convention"] = service.convention
        if service.convention.is_avenant():
            context["form_step"] = self.avenant_stepper.get_form_step(
                step_number=self.step_number
            )
        else:
            context["form_step"] = self.convention_stepper.get_form_step(
                step_number=self.step_number
            )

        if hasattr(service, "form"):
            context["form"] = service.form
        return context

    @currentrole_campaign_permission_required("convention.validate_convention")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @currentrole_campaign_permission_required("convention.validate_convention")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FinalisationNumero(FinalisationBase):
    template_name = "conventions/finalisation/numero.html"
    step_number = 1
    service_class = FinalisationNumeroService

    @currentrole_campaign_permission_required("convention.validate_convention")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context["convention"].is_avenant():
            context["numero_default"] = context[
                "convention"
            ].get_default_convention_number()
        return context


class FinalisationCerfa(FinalisationBase):
    template_name = "conventions/finalisation/cerfa.html"
    step_number = 2
    service_class = FinalisationCerfaService

    @currentrole_campaign_permission_required("convention.change_convention")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fichier_cerfa = context["convention"].fichier_override_cerfa
        if fichier_cerfa and fichier_cerfa != "{}":
            files_dict = json.loads(fichier_cerfa)
            files = list(files_dict["files"].values())
            context["cerfa_expanded"] = "true" if len(files) > 0 else "false"
        else:
            context["cerfa_expanded"] = "false"
        return context


class FinalisationValidation(FinalisationBase):
    template_name = "conventions/finalisation/validation.html"
    step_number = 3
    service_class = FinalisationValidationService
