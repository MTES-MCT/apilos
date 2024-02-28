from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from waffle.mixins import WaffleFlagMixin

from conventions.services.add import ConventionAddService


class SelectOperationView(WaffleFlagMixin, LoginRequiredMixin, TemplateView):
    waffle_flag = settings.FLAG_ADD_CONVENTION
    template_name = "conventions/select_operation.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx.update({})


class AddConventionView(WaffleFlagMixin, LoginRequiredMixin, TemplateView):
    waffle_flag = settings.FLAG_ADD_CONVENTION
    template_name = "conventions/add_convention.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        service = ConventionAddService(self.request)
        ctx = super().get_context_data(**kwargs)
        ctx.update({"form": service.get_form()})
