from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import (
    ContextMixin,
    TemplateResponseMixin,
    TemplateView,
    View,
)
from waffle.mixins import WaffleFlagMixin

from conventions.models import Convention
from conventions.services import utils
from conventions.services.from_operation import (
    AddAvenantsService,
    AddConventionService,
    SelectOperationService,
)


class Stepper:
    steps: list[str]

    def __init__(self) -> None:
        self.steps = [
            "Sélectioner l'opération",
            "Créer la convention dans Apilos",
            "Ajouter les avenants (optionnel)",
        ]

    def get_form_step(self, step_number: int) -> dict[str, Any] | None:
        count_steps = len(self.steps)
        if step_number < 1 or step_number > count_steps:
            return None
        return {
            "number": step_number,
            "total": count_steps,
            "current_step": self.steps[step_number - 1],
            "next_step": self.steps[step_number] if step_number < count_steps else None,
        }


class AddConventionFromOperationBaseView(WaffleFlagMixin, LoginRequiredMixin, View):
    waffle_flag = settings.FLAG_ADD_CONVENTION
    stepper: Stepper
    step_number: int

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)
        self.stepper = Stepper()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        return super().get_context_data(**kwargs) | {
            "form_step": self.stepper.get_form_step(step_number=self.step_number)
        }


class SelectOperationView(AddConventionFromOperationBaseView, TemplateView):
    template_name = "conventions/from_operation/select_operation.html"
    step_number = 1

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        exact_match, operations = SelectOperationService(
            request=self.request,
            numero_operation=self.request.GET.get("numero_operation"),
        ).fetch_operations()

        return super().get_context_data(**kwargs) | {
            "operations": operations,
            "siap_assistance_url": settings.SIAP_ASSISTANCE_URL,
            "exact_match": exact_match,
        }


class AddConventionView(
    AddConventionFromOperationBaseView, TemplateResponseMixin, ContextMixin, View
):
    template_name = "conventions/from_operation/add_convention.html"
    step_number = 2

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self._handle(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self._handle(request, *args, **kwargs)

    def _handle(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        numero_operation = kwargs.get("numero_operation")

        #  TODO: handle null operation and user rights
        operation = SelectOperationService(
            request=request, numero_operation=numero_operation
        ).get_operation()

        service = AddConventionService(request=request, operation=operation)
        if request.method == "POST":
            service.save()
            if (
                service.return_status == utils.ReturnStatus.SUCCESS
                and service.convention
            ):
                return HttpResponseRedirect(
                    reverse(
                        "conventions:from_operation_add_avenants",
                        kwargs={"convention_uuid": service.convention.uuid},
                    )
                )

        context = self.get_context_data(**kwargs) | {
            "form": service.form,
            "operation": operation,
        }
        return self.render_to_response(context=context)


class AddAvenantsView(
    AddConventionFromOperationBaseView, TemplateResponseMixin, ContextMixin, View
):
    template_name = "conventions/from_operation/add_avenants.html"
    step_number = 3

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self._handle(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self._handle(request, *args, **kwargs)

    def _handle(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        convention = get_object_or_404(Convention, uuid=kwargs.get("convention_uuid"))

        service = AddAvenantsService(request=self.request, convention=convention)
        if request.method == "POST":
            service.save()

        context = self.get_context_data(**kwargs) | {
            "formset": service.formset,
            "convention": convention,
        }
        return self.render_to_response(context=context)
