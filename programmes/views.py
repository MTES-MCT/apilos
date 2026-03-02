import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe
from django.views.generic import TemplateView
from waffle import switch_is_active

from conventions.models import Convention, ConventionGroupingError, ConventionStatut
from conventions.services.search import (
    ConventionSearchService,
    OperationConventionSearchService,
    ProgrammeConventionSearchService,
)
from programmes.models.models import Programme
from programmes.services import OperationService
from siap.exceptions import DuplicatedOperationSIAPException

logger = logging.getLogger(__name__)


def _handle_seconde_vie(request, operation_service, numero_operation):
    """Return an HttpResponse if the operation is Seconde Vie, else None."""
    if not operation_service.is_seconde_vie():
        return None

    if switch_is_active(settings.SWITCH_SECONDE_VIE_ON):
        has_sv_with_parents = Convention.objects.filter(
            programme__numero_operation=numero_operation,
            parents__isnull=False,
        ).exists()
        if not has_sv_with_parents:
            return HttpResponseRedirect(
                reverse("programmes:seconde_vie_existing", args=[numero_operation])
            )
        return None

    # Feature flag off — show a notice, do not create any conventions
    service = OperationConventionSearchService(numero_operation)
    paginator = service.paginate()
    context = operation_service.get_context_list_conventions(paginator=paginator)
    context["switch_convention_mixte_on"] = False
    context["is_seconde_vie"] = True
    context["seconde_vie_feature_disabled"] = True
    return render(request, "operations/conventions.html", context)


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
    sv_response = _handle_seconde_vie(request, operation_service, numero_operation)
    if sv_response is not None:
        return sv_response

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
    context["switch_convention_mixte_on"] = switch_is_active(
        settings.SWITCH_CONVENTION_MIXTE_ON
    )
    context["is_seconde_vie"] = operation_service.is_seconde_vie()
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

        is_readonly = (
            "readonly" in self.request.session and self.request.session["readonly"]
        )

        # For readonly users without SIAP access, try to get existing programme
        if is_readonly and service.operation is None:
            try:
                context["programme"] = Programme.objects.filter(
                    numero_operation=kwargs["numero_operation"]
                ).first()
                context["is_seconde_vie"] = (
                    context["programme"].seconde_vie if context["programme"] else False
                )
            except Programme.DoesNotExist:
                context["programme"] = None
                context["is_seconde_vie"] = False
        else:
            context["programme"] = service.get_or_create_programme()
            context["is_seconde_vie"] = service.is_seconde_vie()

        return context


class SecondeVieExistingView(SecondeVieBaseView):
    template_name = "operations/seconde_vie/existing.html"

    def get(self, request, *args, **kwargs):
        if not switch_is_active(settings.SWITCH_SECONDE_VIE_ON):
            return HttpResponseRedirect(reverse("conventions:search"))

        operation_service = OperationService(
            request=request, numero_operation=kwargs["numero_operation"]
        )

        is_readonly = "readonly" in request.session and request.session["readonly"]

        # CHECK HABILITAION FOR USER
        if operation_service.operation is None:
            # For readonly users, allow access if programme exists in database
            if is_readonly:
                existing_programmes = Programme.objects.filter(
                    numero_operation=kwargs["numero_operation"]
                )
                if not existing_programmes.exists():
                    messages.add_message(
                        request,
                        messages.INFO,
                        f"L'opération {kwargs['numero_operation']} n'existe pas dans APiLos",
                    )
                    return HttpResponseRedirect(
                        reverse("conventions:search")
                        + f"?search_numero={kwargs['numero_operation']}"
                    )
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    f"L'opération {kwargs['numero_operation']} n'existe pas dans le SIAP",
                )
                return HttpResponseRedirect(
                    reverse("conventions:search")
                    + f"?search_numero={kwargs['numero_operation']}"
                )

        context = self.get_context_data(**kwargs)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(
                request, "operations/seconde_vie/_search_results.html", context
            )
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        status_filter = self.request.GET.get("status")

        # Existing Seconde Vie convention for this programme
        programme = context["programme"]
        seconde_vie_convention = None
        if programme:
            # Prefer a convention already linked to parents
            seconde_vie_convention = Convention.objects.filter(
                programme=programme, parents__isnull=False
            ).first()

            if not seconde_vie_convention and programme.seconde_vie:
                seconde_vie_convention = (
                    Convention.objects.filter(programme=programme, parent__isnull=True)
                    .order_by("-cree_le")
                    .first()
                )

        context["has_seconde_vie_convention"] = bool(seconde_vie_convention)
        context["seconde_vie_convention_uuid"] = (
            str(seconde_vie_convention.uuid) if seconde_vie_convention else None
        )

        # Get pre-selected parent UUIDs from query parameters (for edit mode)
        pre_selected_uuids = self.request.GET.getlist("parent_uuid")
        pre_selected_conventions = []
        if pre_selected_uuids:
            pre_selected_conventions = list(
                Convention.objects.filter(uuid__in=pre_selected_uuids)
            )
        elif seconde_vie_convention:
            pre_selected_conventions = list(seconde_vie_convention.parents.all())

        context["pre_selected_conventions"] = pre_selected_conventions

        if query:
            filters = {}
            service = ConventionSearchService(self.request.user, filters)

            queryset = service.get_queryset().exclude(programme=context["programme"])

            allowed_statuses = [
                ConventionStatut.SIGNEE.label,
                ConventionStatut.PUBLICATION_EN_COURS.label,
                ConventionStatut.PUBLIE.label,
            ]

            # Apply status filter if provided
            if status_filter:
                queryset = queryset.filter(statut=status_filter)
            else:
                queryset = queryset.filter(statut__in=allowed_statuses)

            # Only non-avenants (parent is None and parents is empty)
            queryset = queryset.filter(parent__isnull=True).exclude(
                id__in=Convention.objects.filter(parents__isnull=False).values_list(
                    "id", flat=True
                )
            )

            # Search by numero, programme name, or ville
            conventions_queryset = (
                queryset.filter(
                    Q(numero__icontains=query)
                    | Q(programme__nom__icontains=query)
                    | Q(programme__ville__icontains=query)
                )
                .select_related("programme")
                .distinct()
            )

            page_number = self.request.GET.get("page", 1)
            paginator = Paginator(conventions_queryset, 10)
            page_obj = paginator.get_page(page_number)

            context["conventions"] = page_obj
            context["query"] = query
        context["status_filter"] = status_filter

        context["is_readonly"] = (
            "readonly" in self.request.session and self.request.session["readonly"]
        )

        return context

    def _create_and_link_conventions(
        self, selected_conventions, target_programme, operation_service
    ):
        """Create conventions for each financement and link them to parents."""

        new_convention_uuids = []

        conventions_by_financements = (
            operation_service.collect_conventions_by_financements()
        )

        # Create conventions for each financement
        for financement, conventions in conventions_by_financements.items():
            if len(conventions) == 0:
                operation_service.create_convention_by_financement(
                    target_programme, financement
                )

        # Refresh and find newly created conventions
        updated_conventions_by_financements = (
            operation_service.collect_conventions_by_financements()
        )

        for financement, conventions in updated_conventions_by_financements.items():
            original_count = len(conventions_by_financements.get(financement, []))
            if len(conventions) > original_count:
                for convention in conventions:
                    if convention not in conventions_by_financements.get(
                        financement, []
                    ):
                        new_convention_uuids.append(str(convention.uuid))
                        convention.parents.set(selected_conventions)
                        convention.save()

        return new_convention_uuids

    def _group_or_get_final_convention(self, new_convention_uuids):
        """Group conventions as mixte if multiple, otherwise get single."""

        final_convention = None

        if len(new_convention_uuids) > 1:
            try:
                _, _, final_convention = Convention.objects.group_conventions(
                    new_convention_uuids
                )
            except ConventionGroupingError:
                # If grouping fails, use first convention
                final_convention = Convention.objects.get(uuid=new_convention_uuids[0])
        elif len(new_convention_uuids) == 1:
            final_convention = Convention.objects.get(uuid=new_convention_uuids[0])

        return final_convention

    def _extract_selected_uuids(self, request, context):
        raw = request.POST.get("selected_conventions")
        selected = [uuid for uuid in raw.split(",") if uuid] if raw is not None else []

        if raw is None and not selected and context.get("seconde_vie_convention_uuid"):
            existing_sv = Convention.objects.filter(
                uuid=context["seconde_vie_convention_uuid"]
            ).first()
            if existing_sv:
                selected = list(existing_sv.parents.values_list("uuid", flat=True))

        return selected

    def _clear_parents_if_empty(self, context, target_programme):
        filters = Q(parents__isnull=False) | Q(seconde_vie_children__isnull=False)
        if context.get("seconde_vie_convention_uuid"):
            filters = filters | Q(uuid=context["seconde_vie_convention_uuid"])

        qs_to_clear = (
            Convention.objects.filter(programme=target_programme)
            .filter(filters)
            .distinct()
        )

        if qs_to_clear.exists():
            for conv in qs_to_clear:
                conv.parents.clear()
            first_cleared = qs_to_clear.first()
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[first_cleared.uuid])
            )

        if target_programme and getattr(target_programme, "seconde_vie", False):
            candidate = (
                Convention.objects.filter(
                    programme=target_programme, parent__isnull=True
                )
                .order_by("-cree_le")
                .first()
            )
            if candidate:
                candidate.parents.clear()
                return HttpResponseRedirect(
                    reverse("conventions:recapitulatif", args=[candidate.uuid])
                )

        return None

    def _update_conventions_with_parents(
        self, selected_uuids, context, target_programme, kwargs
    ):
        with transaction.atomic():
            selected_conventions = list(
                Convention.objects.filter(uuid__in=selected_uuids)
            )
            if not selected_conventions:
                return None

            operation_service = OperationService(
                request=self.request, numero_operation=kwargs["numero_operation"]
            )

            existing_seconde_vie_conventions = Convention.objects.filter(
                programme=target_programme, parents__isnull=False
            ).distinct()

            final_convention = None
            if existing_seconde_vie_conventions.exists():
                for convention in existing_seconde_vie_conventions:
                    convention.parents.set(selected_conventions)
                final_convention = existing_seconde_vie_conventions.first()
            elif context.get("seconde_vie_convention_uuid"):
                final_convention = Convention.objects.filter(
                    uuid=context["seconde_vie_convention_uuid"]
                ).first()
                if final_convention:
                    final_convention.parents.set(selected_conventions)
                    final_convention.save()
            else:
                new_convention_uuids = self._create_and_link_conventions(
                    selected_conventions, target_programme, operation_service
                )
                final_convention = self._group_or_get_final_convention(
                    new_convention_uuids
                )

            return final_convention

    def post(self, request, *args, **kwargs):
        if not switch_is_active(settings.SWITCH_SECONDE_VIE_ON):
            return HttpResponseRedirect(reverse("conventions:search"))

        # Check if user has readonly access
        if "readonly" in request.session and request.session["readonly"]:
            messages.add_message(
                request,
                messages.ERROR,
                "Vous n'avez pas les droits pour effectuer cette action.",
            )
            return HttpResponseRedirect(
                reverse(
                    request.resolver_match.view_name,
                    args=request.resolver_match.args,
                    kwargs=request.resolver_match.kwargs,
                )
            )

        context = self.get_context_data(**kwargs)
        action = request.POST.get("action")
        target_programme = context["programme"]

        if action == "validate":
            selected_uuids = self._extract_selected_uuids(request, context)

            if not selected_uuids:
                cleared_response = self._clear_parents_if_empty(
                    context, target_programme
                )
                if cleared_response:
                    return cleared_response
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Veuillez sélectionner au moins une convention parente avant de valider.",
                )
                return render(request, self.template_name, context)

            final_convention = self._update_conventions_with_parents(
                selected_uuids, context, target_programme, kwargs
            )

            if final_convention:
                return HttpResponseRedirect(
                    reverse("conventions:bailleur", args=[final_convention.uuid])
                )

            return render(request, self.template_name, context)

        return render(request, self.template_name, context)


@login_required
@require_safe
def seconde_vie_new(request, numero_operation):
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    if not switch_is_active(settings.SWITCH_SECONDE_VIE_ON):
        return HttpResponseRedirect(reverse("conventions:search"))

    if "readonly" in request.session and request.session["readonly"]:
        messages.add_message(
            request,
            messages.ERROR,
            "Vous n'avez pas les droits pour créer de nouvelles conventions.",
        )
        return HttpResponseRedirect(reverse("conventions:search"))

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

    new_conventions = Convention.objects.filter(
        programme=programme,
        parent__isnull=True,
        statut="1. Projet",
    ).order_by("-cree_le")

    # Group multiple conventions as mixte convention if needed
    if new_conventions.count() > 1:
        new_convention_uuids = [str(conv.uuid) for conv in new_conventions]
        try:
            programme, lots, final_convention = Convention.objects.group_conventions(
                new_convention_uuids
            )
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[final_convention.uuid])
            )
        except ConventionGroupingError:
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[new_conventions.first().uuid])
            )
    elif new_conventions.count() == 1:
        return HttpResponseRedirect(
            reverse("conventions:bailleur", args=[new_conventions.first().uuid])
        )

    service = ProgrammeConventionSearchService(programme)
    paginator = service.paginate()
    context = operation_service.get_context_list_conventions(paginator=paginator)

    return render(request, "operations/conventions.html", context)
