import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe
from django.views.generic import TemplateView
from waffle import switch_is_active

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
    # For seconde vie, check if there are ANY conventions (including those with parents)
    if operation_service.is_seconde_vie():
        from conventions.models import Convention

        all_conventions = Convention.objects.filter(
            programme__numero_operation=numero_operation
        ).exclude(statut="11. Annulée")

        if not all_conventions.exists():
            # No conventions at all, redirect to selection page
            return HttpResponseRedirect(
                reverse("programmes:seconde_vie_existing", args=[numero_operation])
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
        context["programme"] = service.get_or_create_programme()
        context["is_seconde_vie"] = service.is_seconde_vie()
        return context


class SecondeVieExistingView(SecondeVieBaseView):
    template_name = "operations/seconde_vie/existing.html"

    def get(self, request, *args, **kwargs):
        # Check if conventions already exist for this operation

        operation_service = OperationService(
            request=request, numero_operation=kwargs["numero_operation"]
        )

        # If conventions already exist, redirect to operation conventions page
        if operation_service.has_conventions():
            return HttpResponseRedirect(
                reverse(
                    "operations:operation_conventions",
                    args=[kwargs["numero_operation"]],
                )
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

        if query:
            # Search for conventions across all programmes
            from django.core.paginator import Paginator
            from django.db.models import Q

            from conventions.models import Convention, ConventionStatut
            from conventions.services.search import ConventionSearchService

            filters = {}
            service = ConventionSearchService(self.request.user, filters)

            # Exclude conventions of the current programme
            queryset = service.get_queryset().exclude(programme=context["programme"])

            # Filter by allowed statuses for Seconde Vie
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

            # Pagination
            page_number = self.request.GET.get("page", 1)
            paginator = Paginator(conventions_queryset, 10)
            page_obj = paginator.get_page(page_number)

            context["conventions"] = page_obj
            context["query"] = query
        context["status_filter"] = status_filter

        return context

    def _create_and_link_conventions(
        self, selected_conventions, target_programme, operation_service
    ):
        """Create conventions for each financement and link them to parents."""

        new_convention_uuids = []

        # Collect conventions by financement
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
        from conventions.models import Convention, ConventionGroupingError

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

    def post(self, request, *args, **kwargs):
        from django.db import transaction

        from conventions.models import Convention

        context = self.get_context_data(**kwargs)
        action = request.POST.get("action")
        target_programme = context["programme"]

        if action == "validate":
            selected_uuids_str = request.POST.get("selected_conventions", "")
            selected_uuids = [uuid for uuid in selected_uuids_str.split(",") if uuid]

            if not selected_uuids:
                return render(request, self.template_name, context)

            with transaction.atomic():
                # Get all selected conventions
                selected_conventions = list(
                    Convention.objects.filter(uuid__in=selected_uuids)
                )
                if not selected_conventions:
                    return render(request, self.template_name, context)

                # Initialize operation service
                operation_service = OperationService(
                    request=request, numero_operation=kwargs["numero_operation"]
                )

                # Create conventions and get UUIDs
                new_convention_uuids = self._create_and_link_conventions(
                    selected_conventions, target_programme, operation_service
                )

                # Group or get final convention
                final_convention = self._group_or_get_final_convention(
                    new_convention_uuids
                )

            # Clear logical session if we were using it (optional now)
            if "seconde_vie_selection" in request.session:
                del request.session["seconde_vie_selection"]

            # Redirect to the created/grouped convention
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

    # Get all conventions just created for this programme
    from conventions.models import Convention, ConventionGroupingError

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
            # Redirect to the grouped mixte convention
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[final_convention.uuid])
            )
        except ConventionGroupingError:
            # If grouping fails, redirect to the first convention
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[new_conventions.first().uuid])
            )
    elif new_conventions.count() == 1:
        # Redirect to the single convention
        return HttpResponseRedirect(
            reverse("conventions:bailleur", args=[new_conventions.first().uuid])
        )

    service = ProgrammeConventionSearchService(programme)
    paginator = service.paginate()
    context = operation_service.get_context_list_conventions(paginator=paginator)

    return render(request, "operations/conventions.html", context)
