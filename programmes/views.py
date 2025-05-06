import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe
from django.views.generic import TemplateView

from conventions.services.search import (
    OperationConventionSearchService,
    ProgrammeConventionSearchService,
)
from programmes.models.models import Programme
from programmes.services import OperationService
from siap.exceptions import DuplicatedOperationSIAPException

logger = logging.getLogger(__name__)


@login_required
def operation_conventions(request, numero_operation):
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    operation_service = OperationService(
        request=request, numero_operation=numero_operation
    )
    if operation_service.operation is None:
        messages.add_message(
            request,
            messages.INFO,
            f"L'opération {numero_operation} n'existe pas dans le SIAP",
        )

        # TODO: get_operations_from_numero_operation function ?
        operation_service.programmes = list(
            Programme.objects.filter(numero_operation_pour_recherche=numero_operation)
        )
    else:
        operation_service.get_or_create_operation()
        operation_service.check_sans_financement_consistancy()

    # Choix du programme de référence, celui qui va être utilisé pour créer les
    # conventions manquantes
    if len(operation_service.programmes) > 1:
        # on selectionne le programme qui a le plus de convention
        programme = max(
            operation_service.programmes, key=lambda p: len(p.conventions.all())
        )
    elif len(operation_service.programmes) == 1:
        programme = operation_service.programmes[0]
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Aucun programme trouvé : Vérifier que le numéro d'opération est correct",
        )
        return HttpResponseRedirect(
            reverse("conventions:search") + f"?search_numero={numero_operation}"
        )

    # Seconde vie : on ne crée pas les conventions automatiquement
    if operation_service.is_seconde_vie() and not operation_service.has_conventions():
        return render(
            request,
            "operations/seconde_vie/choice.html",
            {
                "programme": programme,
                "is_seconde_vie": operation_service.is_seconde_vie(),
            },
        )

    # collect des conventions par financement
    conventions_by_financements = (
        operation_service.collect_conventions_by_financements()
    )

    for financement, conventions in conventions_by_financements.items():
        if len(conventions) == 0:
            operation_service.create_convention_by_financement(programme, financement)
        elif len(conventions) > 1:
            messages.add_message(
                request,
                messages.WARNING,
                "Il existe plusieurs conventions actives pour le financement"
                f" {financement}, Merci d'annuler les conventions que vous ne"
                " souhaitez pas conserver",
            )

    service = OperationConventionSearchService(numero_operation)
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
@require_safe
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
