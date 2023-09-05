import mimetypes
from datetime import date
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import resolve, reverse
from django.views import View
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from conventions.forms.convention_form_administration import (
    UpdateConventionAdministrationForm,
)
from conventions.forms.convention_form_simulateur_loyer import LoyerSimulateurForm
from conventions.forms.evenement import EvenementForm
from conventions.models import Convention, ConventionStatut, Evenement, PieceJointe
from conventions.permissions import (
    has_campaign_permission,
    has_campaign_permission_view_function,
)
from conventions.services import convention_generator
from conventions.services.convention_generator import fiche_caf_doc
from conventions.services.conventions import convention_post_action, convention_sent
from conventions.services.file import ConventionFileService
from conventions.services.recapitulatif import (
    ConventionRecapitulatifService,
    convention_feedback,
    convention_submit,
    convention_validate,
)
from conventions.services.search import (
    UserConventionActivesSearchService,
    UserConventionEnInstructionSearchService,
    UserConventionSearchService,
    UserConventionTermineesSearchService,
)
from conventions.services.utils import ReturnStatus, base_convention_response_error
from conventions.views.convention_form import BaseConventionView, ConventionFormSteps
from core.storage import client
from programmes.models import Financement, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer
from upload.services import UploadService
from users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User


def get_forms_for_convention(convention: Convention, *args):
    """Regroupe tous les formulaires utilisés sur la vue recapitulatif.
    À terme, tous les formulaires définis sur ConventionRecapitulatifService
    pourraient être définis ici pour éviter de mélanger business logic et affichage
    """
    return {
        "update_convention_administration_form": UpdateConventionAdministrationForm(
            initial={
                "administration": convention.programme.administration,
                "convention": convention.pk,
            },
            *args,
        )
    }


class RecapitulatifView(BaseConventionView):
    forms: dict

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related(
                "programme__referencecadastrales",
                "programme__logementedds",
                "lot",
                "lot__type_stationnements",
                "lot__logements",
                "programme__administration",
            )
            .get(uuid=convention_uuid)
        )

    def _get_forms(self, *args):
        return get_forms_for_convention(self.convention, *args)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            self.forms = self._get_forms()

    @has_campaign_permission("convention.view_convention")
    def get(self, request: HttpRequest, **kwargs):
        service = ConventionRecapitulatifService(
            request=request, convention=self.convention
        )
        result = service.get_convention_recapitulatif()

        if self.convention.is_avenant():
            result["avenant_list"] = [
                avenant_type.nom for avenant_type in self.convention.avenant_types.all()
            ]

        return render(
            request,
            "conventions/recapitulatif.html",
            {
                **base_convention_response_error(request, self.convention),
                **result,
                **self.forms,
                "convention_form_steps": ConventionFormSteps(
                    convention=self.convention
                ),
            },
        )

    @has_campaign_permission("convention.change_convention")
    def post(self, request: HttpRequest, **kwargs):
        self.forms = self._get_forms(request.POST)

        for _, form in self.forms.items():
            if form.is_valid():
                # TODO : gérer plusieurs formulaires valides ici
                return form.submit(request)

        service = ConventionRecapitulatifService(
            request=request, convention=self.convention
        )

        if request.POST.get("update_programme_number"):
            result = service.update_programme_number()
        elif request.POST.get("cancel_convention"):
            result = service.cancel_convention()
        elif request.POST.get("reactive_convention"):
            result = service.reactive_convention()
        else:
            result = service.save_convention_TypeIandII()

        return render(
            request,
            "conventions/recapitulatif.html",
            {
                **base_convention_response_error(request, self.convention),
                **result,
                **self.forms,
                "convention_form_steps": ConventionFormSteps(
                    convention=self.convention
                ),
            },
        )


class ConventionTabsMixin:
    def get_tab(self, subclass):
        service = subclass.service_class(
            user=self.request.user,
        )

        url = reverse(f"conventions:{subclass.name}")

        return {
            "title": subclass.service_class.verbose_name,
            "url": url,
            "weight": subclass.service_class.weight,
            "count": service.get_queryset().count(),
        }

    def get_tabs(self):
        return sorted(
            [
                self.get_tab(subclass)
                for subclass in ConventionSearchView.__subclasses__()
            ],
            key=lambda tab: tab["weight"],
        )


class ConventionSearchView(LoginRequiredMixin, ConventionTabsMixin, View):
    service: UserConventionSearchService
    service_class: type[UserConventionSearchService]
    statuses: list
    order_by: str

    def setup(self, *args, **kwargs) -> None:
        super().setup(*args, **kwargs)

        search_filters_mapping = [
            ("commune", "ville"),
            ("departement", "departement_input"),
            ("financement", "financement"),
            ("order_by", "order_by"),
            ("search_input", "search_input"),
            ("statut", "cstatut"),
            ("bailleur", "bailleur"),
            ("administration", "administration"),
        ]
        search_filters = {
            arg: self._get_non_empty_query_param(query_param)
            for arg, query_param in search_filters_mapping
        }

        self.service = self.service_class(
            anru=(self.request.GET.get("anru") is not None),
            user=self.request.user,
            search_filters=search_filters,
        )

    @property
    def bailleurs_queryset(self) -> QuerySet | None:
        user = self.request.user
        if user.is_instructeur():
            return user.bailleurs(full_scope=True).exclude(nom__exact="")[
                : settings.APILOS_MAX_DROPDOWN_COUNT
            ]

        return None

    @property
    def administrations_queryset(self) -> QuerySet | None:
        user = self.request.user

        if user.is_bailleur():
            return user.administrations()[: settings.APILOS_MAX_DROPDOWN_COUNT]

        return None

    @property
    def all_conventions_count(self):
        return sum(tab["count"] for tab in self.get_tabs())

    def _get_non_empty_query_param(self, query_param: str, default=None) -> str | None:
        if value := self.request.GET.get(query_param):
            return value

        return default

    def get(self, request: AuthenticatedHttpRequest):
        paginator = self.service.paginate()

        return render(
            request,
            "conventions/index.html",
            {
                "administration_query": self.administrations_queryset,
                "all_conventions_count": self.all_conventions_count,
                "bailleur_query": self.bailleurs_queryset,
                "conventions": paginator.get_page(request.GET.get("page", 1)),
                "filtered_conventions_count": paginator.count,
                "financements": Financement.choices,
                "url_name": resolve(request.path_info).url_name,
                "search_input": self._get_non_empty_query_param("search_input", ""),
                "statuts": self.service.choices,
                "tabs": self.get_tabs(),
                "total_conventions": request.user.conventions().count(),
                "order_by": self._get_non_empty_query_param("order_by", ""),
            },
        )


class ConventionEnInstructionSearchView(ConventionSearchView):
    service_class = UserConventionEnInstructionSearchService
    name = "search_instruction"


class ConventionActivesSearchView(ConventionSearchView):
    service_class = UserConventionActivesSearchService
    name = "search_active"


class ConventionTermineesSearchView(ConventionSearchView):
    service_class = UserConventionTermineesSearchService
    name = "search_resiliees"


class LoyerSimulateurView(LoginRequiredMixin, ConventionTabsMixin, View):
    def post(self, request: AuthenticatedHttpRequest):
        loyer_simulateur_form = LoyerSimulateurForm(request.POST)
        montant_actualise = None
        annee_validite = None

        if loyer_simulateur_form.is_valid():
            montant_actualise = LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=float(loyer_simulateur_form.cleaned_data["montant"]),
                nature_logement=loyer_simulateur_form.cleaned_data["nature_logement"],
                date_initiale=loyer_simulateur_form.cleaned_data["date_initiale"],
                date_actualisation=loyer_simulateur_form.cleaned_data[
                    "date_actualisation"
                ],
            )

            annee_validite = loyer_simulateur_form.cleaned_data[
                "date_actualisation"
            ].year

        return render(
            request,
            "conventions/calculette_loyer.html",
            {
                "form": loyer_simulateur_form,
                "tabs": self.get_tabs(),
                "montant_actualise": montant_actualise,
                "annee_validite": annee_validite,
            },
        )

    def get(self, request: AuthenticatedHttpRequest):
        loyer_simulateur_form = LoyerSimulateurForm(
            initial=dict(
                date_actualisation=date.today().isoformat(),
                nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            )
        )

        return render(
            request,
            "conventions/calculette_loyer.html",
            {
                "form": loyer_simulateur_form,
                "tabs": self.get_tabs(),
            },
        )


@require_POST
@login_required
@has_campaign_permission_view_function("convention.change_convention")
def save_convention(request, convention_uuid):
    # could be in a summary service
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.change_convention", convention)
    result = convention_submit(request, convention)
    if result["success"] in [ReturnStatus.SUCCESS, ReturnStatus.WARNING]:
        result.update(
            {"siap_operation_not_found": result["success"] == ReturnStatus.WARNING}
        )
        return render(
            request,
            "conventions/submitted.html",
            result,
        )
    if result["success"] == ReturnStatus.REFRESH:
        return render(
            request,
            "conventions/saved.html",
            result,
        )
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


@require_POST
@login_required
@has_campaign_permission_view_function("convention.delete_convention")
def delete_convention(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    convention.delete()
    return HttpResponseRedirect(reverse("conventions:index"))


@require_POST
@login_required
@has_campaign_permission_view_function("convention.change_convention")
def feedback_convention(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.view_convention", convention)
    result = convention_feedback(request, convention)
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


@require_POST
@login_required
@has_campaign_permission_view_function("convention.change_convention")
def validate_convention(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("programme__bailleur")
        .prefetch_related("programme__referencecadastrales")
        .prefetch_related("programme__logementedds")
        .prefetch_related("lot")
        .prefetch_related("lot__type_stationnements")
        .prefetch_related("lot__logements")
        .get(uuid=convention_uuid)
    )
    request.user.check_perm("convention.change_convention", convention)
    result = convention_validate(request, convention)
    is_complete_avenant_form = request.POST.get("completeform", False)
    if is_complete_avenant_form:
        if result["success"] == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
    else:
        if result["success"] == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:sent", args=[result["convention"].uuid])
            )
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
            "convention_form_steps": ConventionFormSteps(convention=convention),
        },
    )


@login_required
@require_POST
@has_campaign_permission_view_function("convention.view_convention")
def generate_convention(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("programme__bailleur")
        .prefetch_related("lot")
        .prefetch_related("lot__type_stationnements")
        .prefetch_related("lot__logements")
        .prefetch_related("prets")
        .prefetch_related("programme")
        .prefetch_related("programme__administration")
        .prefetch_related("programme__logementedds")
        .prefetch_related("programme__referencecadastrales")
        .get(uuid=convention_uuid)
    )
    request.user.check_perm("convention.view_convention", convention)

    data = convention_generator.generate_convention_doc(convention)

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename={convention}.docx"
    return response


@login_required
def load_xlsx_model(request, file_type):
    if file_type not in [
        "all",
        "annexes",
        "cadastre",
        "financement",
        "locaux_collectifs",
        "foyer_residence_logements",
        "listing_bailleur",
        "logements_edd",
        "logements",
        "stationnements",
    ]:
        raise PermissionDenied

    if file_type == "all":
        filepath = (
            settings.BASE_DIR / "static" / "files" / "tous_les_templates_xlsx.zip"
        )
        with ZipFile(filepath, "w") as zipObj:
            # Add multiple files to the zip
            for each_file in [
                "annexes",
                "cadastre",
                "financement",
                "logements_edd",
                "logements",
                "stationnements",
            ]:
                zipObj.write(
                    f"{settings.BASE_DIR}/static/files/{each_file}.xlsx",
                    arcname=f"{each_file}.xlsx",
                )
            zipObj.close()
        with open(filepath, "rb") as zip_file:
            # close the Zip File
            response = HttpResponse(zip_file, content_type="application/force-download")
            zip_file.close()
        response[
            "Content-Disposition"
        ] = 'attachment; filename="tous_les_templates_xlsx.zip"'
        return response

    filepath = settings.BASE_DIR / "static" / "files" / f"{file_type}.xlsx"

    with open(filepath, "rb") as excel:
        data = excel.read()

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename={file_type}.xlsx"
    return response


@require_GET
@login_required
@has_campaign_permission_view_function("convention.view_convention")
def preview(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.view_convention", convention)
    return render(
        request,
        "conventions/preview.html",
        {"convention": convention},
    )


@login_required
@has_campaign_permission_view_function("convention.change_convention")
def sent(request, convention_uuid, *args):
    result = convention_sent(request, convention_uuid)
    convention = Convention.objects.get(uuid=convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:preview", args=[convention_uuid])
        )

    return render(
        request,
        "conventions/sent.html",
        {
            **result,
            "convention": convention,
            **get_forms_for_convention(convention, *args),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
@has_campaign_permission_view_function("convention.change_convention")
def post_action(request, convention_uuid):
    # Step 12/12
    result = convention_post_action(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result["form_posted"] == "resiliation":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[convention_uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:post_action", args=[convention_uuid])
        )
    return render(
        request,
        "conventions/post_action.html",
        {
            **result,
        },
    )


@login_required
@has_campaign_permission_view_function("convention.view_convention")
def display_pdf(request, convention_uuid):
    # récupérer le doc PDF
    convention = Convention.objects.get(uuid=convention_uuid)
    filename = None
    if (
        convention.statut
        in [
            ConventionStatut.SIGNEE.label,
            ConventionStatut.RESILIEE.label,
            ConventionStatut.DENONCEE.label,
            ConventionStatut.ANNULEE.label,
        ]
        and convention.nom_fichier_signe
        and default_storage.exists(
            f"conventions/{convention.uuid}/convention_docs/{convention.nom_fichier_signe}"
        )
    ):
        filename = convention.nom_fichier_signe
    elif default_storage.exists(
        f"conventions/{convention.uuid}/convention_docs/{convention.uuid}.pdf"
    ):
        filename = f"{convention.uuid}.pdf"
    elif default_storage.exists(
        f"conventions/{convention.uuid}/convention_docs/{convention.uuid}.docx"
    ):
        filename = f"{convention.uuid}.docx"
    if filename:
        return FileResponse(
            UploadService(
                convention_dirpath=f"conventions/{convention.uuid}/convention_docs",
                filename=filename,
            ).get_file(),
            filename=filename,
        )

    return render(
        request,
        "conventions/no_convention_document.html",
    )


@require_http_methods(["GET", "POST"])
@login_required
def journal(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    action = None
    form = None
    selected = None

    if request.method == "POST":
        action = request.POST.get("action")
        # Show create form
        if action == "create":
            form = EvenementForm()
        # Show edit form
        if action == "edit":
            selected = Evenement.objects.filter(
                convention=convention, uuid=request.POST.get("evenement")
            ).first()
            form = EvenementForm(
                initial=dict(
                    uuid=selected.uuid,
                    description=selected.description,
                    type_evenement=selected.type_evenement,
                )
            )
        # Handle submitted data
        if action == "submit":
            form = EvenementForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["uuid"] is not None:
                    evenement = Evenement.objects.get(uuid=form.cleaned_data["uuid"])
                    evenement.description = form.cleaned_data["description"]
                    evenement.type_evenement = form.cleaned_data["type_evenement"]
                    evenement.save()
                else:
                    Evenement.objects.create(
                        convention=convention,
                        description=form.cleaned_data["description"],
                        type_evenement=form.cleaned_data["type_evenement"],
                    )

    return render(
        request,
        "conventions/journal.html",
        {
            "convention": convention,
            "action": action,
            "form": form,
            "selected": selected,
            "events": convention.evenements.all().order_by("-survenu_le"),
        },
    )


@login_required
@require_GET
@has_campaign_permission_view_function("convention.view_convention")
def fiche_caf(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__logements")
        .prefetch_related("programme")
        .prefetch_related("programme__administration")
        .get(uuid=convention_uuid)
    )
    file_stream = fiche_caf_doc(convention)

    response = HttpResponse(
        file_stream,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename=ficheCAF_{convention}.docx"
    return response


@login_required
@require_GET
@permission_required("convention.add_convention")
def piece_jointe_access(request, piece_jointe_uuid):
    """
    Display the raw file associated to the pièce jointe
    """
    piece_jointe_from_db = PieceJointe.objects.get(uuid=piece_jointe_uuid)

    try:
        file: File = client.get_object(
            settings.AWS_ECOLOWEB_BUCKET_NAME,
            f"piecesJointes/{piece_jointe_from_db.fichier}",
        )

        return FileResponse(
            file,
            filename=piece_jointe_from_db.nom_reel,
            content_type=mimetypes.guess_type(piece_jointe_from_db.fichier)[0],
        )
    except FileNotFoundError:
        return HttpResponseNotFound()


@login_required
@permission_required("convention.add_convention")
def piece_jointe_promote(request, piece_jointe_uuid):
    """
    Promote a pièce jointe to the official PDF document of a convention
    """
    piece_jointe = PieceJointe.objects.get(uuid=piece_jointe_uuid)

    if piece_jointe is None:
        return HttpResponseNotFound

    if piece_jointe.convention.ecolo_reference is None:
        return HttpResponseForbidden()

    if not piece_jointe.is_promotable():
        return HttpResponseForbidden()

    ConventionFileService.promote_piece_jointe(piece_jointe)
    return HttpResponseRedirect(
        reverse("conventions:preview", args=[piece_jointe.convention.uuid])
    )


@login_required
@permission_required("convention.change_convention")
def expert_mode(request, convention_uuid):
    if "is_expert" in request.session and request.session["is_expert"] is True:
        request.session["is_expert"] = False
    else:
        request.session["is_expert"] = True
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[convention_uuid])
    )
