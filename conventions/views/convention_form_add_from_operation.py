from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from waffle.mixins import WaffleFlagMixin

from conventions.services.add_from_operation import (
    ConventionAddService,
    SelectOperationService,
)


class SelectOperationView(WaffleFlagMixin, LoginRequiredMixin, TemplateView):
    waffle_flag = settings.FLAG_ADD_CONVENTION
    template_name = "conventions/select_operation.html"

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


class AddConventionFromOperationView(WaffleFlagMixin, LoginRequiredMixin, TemplateView):
    waffle_flag = settings.FLAG_ADD_CONVENTION
    template_name = "conventions/add_from_operation.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        service = ConventionAddService(self.request)
        ctx = super().get_context_data(**kwargs)
        ctx.update({"form": service.get_form()})
