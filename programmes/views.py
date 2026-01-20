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
    context["switch_convention_mixte_on"] = switch_is_active(
        settings.SWITCH_CONVENTION_MIXTE_ON
    )
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

    def _clone_lot_with_children(self, lot, new_convention):
        """Clone a lot and its children (Logements, RepartitionSurface) to a new convention."""
        from programmes.models.models import RepartitionSurface

        new_lot = lot.clone(new_convention)

        # Clone children (Logements)
        for logement in lot.logements.all():
            logement.clone(new_lot)

        # Clone RepartitionSurface
        for surface in lot.surfaces.all():
            RepartitionSurface.objects.create(
                lot=new_lot,
                typologie=surface.typologie,
                type_habitat=surface.type_habitat,
                quantite=surface.quantite,
            )
        return new_lot

    def _merge_lot_into_existing(self, lot, existing_lot):
        """Merge a lot's data into an existing lot with the same financement."""
        from programmes.models.models import RepartitionSurface

        # Sum numeric fields
        existing_lot.nb_logements = (existing_lot.nb_logements or 0) + (
            lot.nb_logements or 0
        )
        existing_lot.surface_habitable_totale = (
            existing_lot.surface_habitable_totale or 0
        ) + (lot.surface_habitable_totale or 0)
        existing_lot.surface_locaux_collectifs_residentiels = (
            existing_lot.surface_locaux_collectifs_residentiels or 0
        ) + (lot.surface_locaux_collectifs_residentiels or 0)
        existing_lot.lgts_mixite_sociale_negocies = (
            existing_lot.lgts_mixite_sociale_negocies or 0
        ) + (lot.lgts_mixite_sociale_negocies or 0)
        existing_lot.save()

        # Clone Logements and attach to existing lot
        for logement in lot.logements.all():
            logement.clone(existing_lot)

        # Merge RepartitionSurface
        for surface in lot.surfaces.all():
            existing_surface = existing_lot.surfaces.filter(
                typologie=surface.typologie,
                type_habitat=surface.type_habitat,
            ).first()

            if existing_surface:
                existing_surface.quantite += surface.quantite
                existing_surface.save()
            else:
                RepartitionSurface.objects.create(
                    lot=existing_lot,
                    typologie=surface.typologie,
                    type_habitat=surface.type_habitat,
                    quantite=surface.quantite,
                )

    def _merge_lots_from_conventions(self, selected_conventions, new_convention):
        """Merge lots from parent conventions into the new convention."""
        merged_lots_by_financement = {}

        for parent in selected_conventions:
            for lot in parent.lots.all():
                if lot.financement not in merged_lots_by_financement:
                    new_lot = self._clone_lot_with_children(lot, new_convention)
                    merged_lots_by_financement[lot.financement] = new_lot
                else:
                    existing_lot = merged_lots_by_financement[lot.financement]
                    self._merge_lot_into_existing(lot, existing_lot)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(
                request, "operations/seconde_vie/_search_results.html", context
            )
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        from django.db import transaction
        from django.forms import model_to_dict

        from conventions.models import Convention, ConventionStatut

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

                # Use the first one as template
                template_convention = selected_conventions[0]

                # Create new convention from template
                convention_fields = model_to_dict(
                    template_convention,
                    exclude=[
                        "id",
                        "uuid",
                        "programme",
                        "pk",
                        "avenant_types",
                        "commentaires",
                        "statut",
                        "cree_le",
                        "mis_a_jour_le",
                        "numero",
                        "parent",
                        "parents",
                        "cree_par",
                        "valide_le",
                        "televersement_convention_signee_le",
                        "donnees_validees",
                        "nom_fichier_signe",
                        "soumis_le",
                        "premiere_soumission_le",
                    ],
                )
                convention_fields["programme"] = target_programme
                convention_fields["cree_par"] = request.user
                convention_fields["statut"] = ConventionStatut.PROJET.label

                new_convention = Convention.objects.create(**convention_fields)

                # Link to all parent conventions
                new_convention.parents.set(selected_conventions)
                new_convention.save()

                # Merge lots from parent conventions
                self._merge_lots_from_conventions(selected_conventions, new_convention)

            # Clear logical session if we were using it (optional now)
            if "seconde_vie_selection" in request.session:
                del request.session["seconde_vie_selection"]

            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[new_convention.uuid])
            )

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

    service = ProgrammeConventionSearchService(programme)
    paginator = service.paginate()
    context = operation_service.get_context_list_conventions(paginator=paginator)

    return render(request, "operations/conventions.html", context)
