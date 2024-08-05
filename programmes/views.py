from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from conventions.services.search import ProgrammeConventionSearchService
from programmes.services import OperationService
from siap.exceptions import DuplicatedOperationSIAPException


@login_required
def operation_conventions(request, numero_operation):
    # Décorator ?
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    operation_service = OperationService(
        request=request, numero_operation=numero_operation
    )
    programme = operation_service.get_or_create_programme()

    # Seconde vie : on ne crée pas les conventions automatiquement
    if operation_service.is_seconde_vie():

        # Cas où les conventions ont déjà été crées
        if operation_service.has_conventions():
            service = ProgrammeConventionSearchService(programme)
            paginator = service.paginate()
            context = operation_service.get_context_list_conventions(
                paginator=paginator
            )
            return render(request, "operations/conventions.html", context)

        return render(
            request,
            "operations/seconde_vie/choice.html",
            {
                "programme": programme,
                "is_seconde_vie": operation_service.is_seconde_vie(),
            },
        )

    try:
        (programme, _, _) = operation_service.get_or_create_conventions()
    except DuplicatedOperationSIAPException as exc:
        return HttpResponseRedirect(
            f"{reverse('conventions:search')}?search_numero={exc.numero_operation}"
        )

    service = ProgrammeConventionSearchService(programme)
    paginator = service.paginate()
    context = operation_service.get_context_list_conventions(paginator=paginator)
    return render(
        request,
        "operations/conventions.html",
        context,
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


class SecondeVieExistingView(SecondeVieBaseView):
    template_name = "operations/seconde_vie/existing.html"


@login_required
def seconde_vie_new(request, numero_operation):
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    operation_service = OperationService(
        request=request, numero_operation=numero_operation
    )
    programme = operation_service.get_or_create_programme()

    try:
        (programme, _, _) = operation_service.get_or_create_conventions()
    except DuplicatedOperationSIAPException as exc:
        return HttpResponseRedirect(
            f"{reverse('conventions:search')}?search_numero={exc.numero_operation}"
        )

    service = ProgrammeConventionSearchService(programme)
    paginator = service.paginate()
    context = operation_service.get_context_list_conventions(paginator=paginator)

    return render(request, "operations/conventions.html", context)
