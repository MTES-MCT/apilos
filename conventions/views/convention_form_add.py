from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from waffle.mixins import WaffleFlagMixin


class AddConventionView(WaffleFlagMixin, LoginRequiredMixin, View):
    waffle_flag = settings.FLAG_ADD_CONVENTION

    def get(self, request):
        return render(
            request,
            "conventions/add_convention.html",
            {},
        )
