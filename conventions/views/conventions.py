import mimetypes
from abc import abstractmethod
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

from bailleurs.models import Bailleur
from conventions.forms.convention_form_simulateur_loyer import LoyerSimulateurForm
from conventions.forms.evenement import EvenementForm
from conventions.models import Convention, ConventionStatut, Evenement, PieceJointe
from conventions.permissions import (
    has_campaign_permission,
    has_campaign_permission_view_function,
)
from conventions.services import convention_generator
from conventions.services.avenants import convention_post_action
from conventions.services.convention_generator import fiche_caf_doc
from conventions.services.conventions import convention_sent
from conventions.services.file import ConventionFileService
from conventions.services.recapitulatif import (
    ConventionRecapitulatifService,
    convention_feedback,
    convention_submit,
    convention_validate,
)
from conventions.services.search import UserConventionSearchService
from conventions.services.utils import ReturnStatus, base_convention_response_error
from conventions.views.convention_form import BaseConventionView, ConventionFormSteps
from core.storage import client
from core.utils import is_valid_uuid
from instructeurs.models import Administration
from programmes.models import Financement, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer
from upload.services import UploadService
from users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User


class RecapitulatifView(BaseConventionView):
    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("programme__referencecadastrales")
            .prefetch_related("programme__logementedds")
            .prefetch_related("lot")
            .prefetch_related("lot__type_stationnements")
            .prefetch_related("lot__logements")
            .prefetch_related("programme__administration")
            .get(uuid=convention_uuid)
        )

    # pylint: disable=W0613
    @has_campaign_permission("convention.view_convention")
    def get(self, request: HttpRequest, convention_uuid: int):
        # pylint: disable=unused-argument
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
                "convention_form_steps": ConventionFormSteps(
                    convention=self.convention
                ),
            },
        )

    # pylint: disable=W0613
    @has_campaign_permission("convention.change_convention")
    def post(self, request: AuthenticatedHttpRequest, convention_uuid: int):
        # pylint: disable=unused-argument
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
                "convention_form_steps": ConventionFormSteps(
                    convention=self.convention
                ),
            },
        )


class ConventionSearchView(LoginRequiredMixin, View):
    statuses = []
    order_by = None

    @abstractmethod
    def conventions_count(self):
        pass

    @property
    def administration(self) -> Administration | None:
        uuid = self._get_uuid_for("administration")
        return Administration.objects.filter(uuid=uuid).first()

    @property
    def bailleur(self) -> Bailleur | None:
        uuid = self._get_uuid_for("bailleur")
        return Bailleur.objects.filter(uuid=uuid).first()

    @property
    def bailleur_queryset(self) -> QuerySet | None:
        user = self.request.user
        if user.is_instructeur():
            return user.bailleurs(full_scope=True).exclude(nom__exact="")[
                : settings.APILOS_MAX_DROPDOWN_COUNT
            ]

        return None

    @property
    def administration_queryset(self) -> QuerySet | None:
        user = self.request.user

        if user.is_bailleur():
            return user.administrations()[: settings.APILOS_MAX_DROPDOWN_COUNT]

        return None

    @property
    def all_conventions_count(self):
        return sum(tab["count"] for tab in self.get_tabs())

    def _get_uuid_for(self, name: str) -> str | None:
        return (
            self.request.GET.get(name)
            if is_valid_uuid(self.request.GET.get(name))
            else None
        )

    def _user_convention_statuses_choices(self, user: User) -> list[tuple[str, str]]:
        return [
            (
                statut.name,
                statut.value.instructeur.label
                if user.is_instructeur()
                else statut.value.bailleur.label,
            )
            for statut in self.statuses
        ]

    @staticmethod
    def _get_tab_for(subclass):
        try:
            route = reverse(subclass)
        except:  # FIXME : remove
            route = "conventions:search_instruction"

        return {
            "title": subclass.tab_title,
            "count": subclass.count(None),
            "route": route,
            "weight": subclass.weight,
        }

    @staticmethod
    def get_tabs():
        return sorted(
            [
                ConventionSearchView._get_tab_for(subclass)
                for subclass in ConventionSearchView.__subclasses__()
            ],
            key=lambda tab: tab["weight"],
        )

    def get(self, request: AuthenticatedHttpRequest):
        search_service = UserConventionSearchService(
            administration=self.administration,
            anru=(request.GET.get("anru") is not None),
            bailleur=self.bailleur,
            commune=request.GET.get("ville"),
            departement=request.GET.get("departement_input", ""),
            financement=request.GET.get("financement", ""),
            order_by=request.GET.get("order_by", self.order_by),
            search_input=request.GET.get("search_input", ""),
            statuses=self.statuses,
            statut=request.GET.get("cstatut", ""),
            user=request.user,
        )

        paginator = search_service.paginate()

        return render(
            request,
            "conventions/index.html",
            {
                "administration_query": self.administration_queryset,
                "all_conventions_count": self.all_conventions_count,
                "bailleur_query": self.bailleur_queryset,
                "conventions": paginator.get_page(request.GET.get("page", 1)),
                "filtered_conventions_count": paginator.count,
                "financements": Financement.choices,
                "inactive": resolve(request.path_info).url_name == "search_instruction",
                "search_input": request.GET.get("search_input", ""),
                "statuts": ConventionStatut.choices,
                "tabs": self.get_tabs(),
                "total_conventions": request.user.conventions().count(),
            },
        )


class ConventionEnInstructionSearchView(ConventionSearchView):
    weight = 0
    statuses = [ConventionStatut.SIGNEE]
    order_by = "televersement_convention_signee_le"
    tab_title = "en instruction"

    def conventions_count(self):
        return 10


class ConventionActivesSearchView(ConventionSearchView):
    weight = 10
    statuses = [
        ConventionStatut.PROJET,
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
        ConventionStatut.A_SIGNER,
    ]
    order_by = "televersement_convention_signee_le"
    tab_title = "active(s)"

    def conventions_count(self):
        return 10


class ConventionTermineesSearchView(ConventionSearchView):
    weight = 100
    order_by = "programme__date_achevement_compile"
    tab_title = "résiliée(s) ou dénoncée(s)"
    statuses = [
        ConventionStatut.RESILIEE,
        ConventionStatut.DENONCEE,
        ConventionStatut.ANNULEE,
    ]

    def conventions_count(self):
        return 1000


class LoyerSimulateurView(LoginRequiredMixin, View):
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
                "tabs": ConventionSearchView.get_tabs(),
                "montant_actualise": montant_actualise,
                "annee_validite": annee_validite,
                "active_conventions_count": 10,
                "completed_conventions_count": 1000,
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
                "tabs": ConventionSearchView.get_tabs(),
                "active_conventions_count": 10,
                "completed_conventions_count": 1000,
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
def sent(request, convention_uuid):
    result = convention_sent(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:preview", args=[convention_uuid])
        )
    return render(
        request,
        "conventions/sent.html",
        {
            **result,
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
