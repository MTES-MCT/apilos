import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import resolve, reverse
from django.views.generic import TemplateView

from conventions.services.search import ProgrammeConventionSearchService
from programmes.services import OperationService
from siap.exceptions import DuplicatedOperationSIAPException


@login_required
def operation_conventions(request, numero_operation):
    # Décorator ?
    logging.warning("operation_conventions %s", numero_operation)
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    service = OperationService(request=request, numero_operation=numero_operation)
    programme = service.get_or_create_programme()

    if service.is_seconde_vie() and not service.has_seconde_vie_conventions():
        return render(
            request,
            "operations/seconde_vie/choice.html",
            {
                "programme": programme,
                "is_seconde_vie": service.is_seconde_vie(),
            },
        )

    try:
        (programme, _, _) = service.get_or_create_conventions()
    except DuplicatedOperationSIAPException as exc:
        return HttpResponseRedirect(
            f"{reverse('conventions:search')}?search_numero={exc.numero_operation}"
        )

    service = ProgrammeConventionSearchService(programme)
    paginator = service.paginate()

    return render(
        request,
        "operations/conventions.html",
        {
            "url_name": resolve(request.path_info).url_name,
            "order_by": request.GET.get("order_by", ""),
            "numero_operation": numero_operation,
            "programme": programme,
            "conventions": paginator.get_page(request.GET.get("page", 1)),
            "filtered_conventions_count": paginator.count,
            "all_conventions_count": paginator.count,
            "siap_assistance_url": settings.SIAP_ASSISTANCE_URL,
            # FIXME: we can probably remove this and get the values from the request in the template
            "search_operation_nom": "",
            "search_numero": "",
            "search_lieu": "",
        },
    )


class SecondeVieBaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = OperationService(
            request=self.request, numero_operation=kwargs["numero_operation"]
        )
        context["programme"] = service.get_or_create_programme()
        context["is_seconde_vie"] = service.is_seconde_vie()
        return context


class SecondeVieNewView(SecondeVieBaseView):
    template_name = "operations/seconde_vie/new.html"


class SecondeVieExistingView(SecondeVieBaseView):
    template_name = "operations/seconde_vie/existing.html"
