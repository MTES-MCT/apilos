from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.views.generic import TemplateView, View
from waffle.mixins import WaffleFlagMixin

from conventions.services.add_from_operation import (
    ConventionAddService,
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
    template_name = "conventions/add_from_operation/select_operation.html"
    step_number = 1

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        numero_operation = self.request.GET.get("numero_operation")

        exact_match, operations = SelectOperationService(
            request=self.request, numero_operation=numero_operation
        ).fetch_operations()

        return super().get_context_data(**kwargs) | {
            "operations": operations,
            "siap_assistance_url": settings.SIAP_ASSISTANCE_URL,
            "exact_match": exact_match,
        }


class AddConventionFromOperationView(AddConventionFromOperationBaseView, TemplateView):
    template_name = "conventions/add_from_operation/create_convention.html"
    step_number = 2

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        service = ConventionAddService(self.request)
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "form": service.get_form(),
            }
        )
        return ctx
