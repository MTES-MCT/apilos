import io
import json
import mimetypes
from datetime import date
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
from django.shortcuts import get_object_or_404, render
from django.urls import resolve, reverse
from django.views import View
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from unidecode import unidecode
from zipfile import ZipFile

from conventions.forms.convention_form_simulateur_loyer import LoyerSimulateurForm
from conventions.forms.evenement import EvenementForm
from conventions.models import Convention, ConventionStatut, Evenement, PieceJointe
from conventions.permissions import (
    currentrole_campaign_permission_required,
    currentrole_campaign_permission_required_view_function,
    currentrole_permission_required,
)
from conventions.services import convention_generator, utils
from conventions.services.avenants import create_avenant
from conventions.services.convention_generator import fiche_caf_doc
from conventions.services.conventions import convention_post_action
from conventions.services.file import ConventionFileService
from conventions.services.recapitulatif import (
    ConventionRecapitulatifService,
    ConventionSentService,
    ConventionUploadSignedService,
    convention_denonciation_validate,
    convention_feedback,
    convention_resiliation_validate,
    convention_submit,
    convention_validate,
)
from conventions.services.search import ConventionSearchService
from conventions.services.utils import ReturnStatus, base_convention_response_error
from conventions.views.convention_form import BaseConventionView, ConventionFormSteps
from core.request import AuthenticatedHttpRequest
from core.storage import client
from programmes.models import Financement, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer
from upload.models import UploadedFile

template_sent = "conventions/sent.html"


class RecapitulatifView(BaseConventionView):
    forms: dict

    def _get_convention(self, convention_uuid):
        return get_object_or_404(
            Convention.objects.prefetch_related("programme").prefetch_related(
                "programme__referencecadastrales",
                "programme__logementedds",
                # "lot",
                # "lot__type_stationnements",
                # "lot__logements",
                "programme__administration",
            ),
            uuid=convention_uuid,
        )

    @currentrole_campaign_permission_required("convention.view_convention")
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
                "convention_form_steps": ConventionFormSteps(
                    convention=self.convention, request=request
                ),
            },
        )

    @currentrole_campaign_permission_required("convention.change_convention")
    def post(self, request: HttpRequest, **kwargs):
        service = ConventionRecapitulatifService(
            request=request, convention=self.convention
        )

        if request.POST.get("update_programme_number"):
            result = service.update_programme_number()
        elif request.POST.get("update_convention_number"):
            result = service.update_convention_number()
        elif request.POST.get("cancel_convention"):
            result = service.cancel_convention()
        elif request.POST.get("reactive_convention"):
            result = service.reactive_convention()
        else:
            result = service.save_convention_type_1_and_2()

        return render(
            request,
            "conventions/recapitulatif.html",
            {
                **base_convention_response_error(request, self.convention),
                **result,
                "convention_form_steps": ConventionFormSteps(
                    convention=self.convention, request=request
                ),
            },
        )


class ConventionSearchView(LoginRequiredMixin, View):
    def _get_non_empty_query_param(self, query_param: str, default=None) -> str | None:
        if value := self.request.GET.get(query_param):
            return value

        return default

    def setup(self, *args, **kwargs) -> None:
        super().setup(*args, **kwargs)

        search_filters = {
            arg: self._get_non_empty_query_param(query_param)
            for arg, query_param in self.get_search_filters_mapping()
        }

        self.service = ConventionSearchService(
            user=self.request.user, search_filters=search_filters
        )

    @property
    def bailleurs_queryset(self) -> QuerySet:
        return self.request.user.bailleurs(full_scope=True).exclude(nom__exact="")[
            : settings.APILOS_MAX_DROPDOWN_COUNT
        ]

    def get(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        return render(request, "conventions/index.html", self.get_context(request))

    def get_context(self, request: AuthenticatedHttpRequest) -> dict[str, Any]:
        paginator = self.service.paginate()
        return {
            "statut_choices": [
                (member.neutre, member.label) for member in ConventionStatut
            ],
            "date_signature_choices": Convention.date_signature_choices(),
            "financement_choices": Financement.choices,
            "nature_logement_choices": NatureLogement.choices,
            "conventions": paginator.get_page(request.GET.get("page", 1)),
            "filtered_conventions_count": paginator.count,
            "url_name": resolve(request.path_info).url_name,
            "user_has_conventions": bool(
                paginator.count or request.user.conventions().count()
            ),
            "bailleur_query": self.bailleurs_queryset,
            "debug_search_scoring": settings.DEBUG_SEARCH_SCORING,
            "siap_assistance_url": settings.SIAP_ASSISTANCE_URL,
        } | {
            k: self._get_non_empty_query_param(k, default="")
            for k in (
                "order_by",
                "search_operation_nom",
                "search_numero",
                "search_lieu",
            )
        }

    def get_search_filters_mapping(self) -> list[tuple[str, str]]:
        return [
            ("anru", "anru"),
            ("avenant_seulement", "avenant_seulement"),
            ("bailleur", "bailleur"),
            ("date_signature", "date_signature"),
            ("financement", "financement"),
            ("nature_logement", "nature_logement"),
            ("order_by", "order_by"),
            ("search_lieu", "search_lieu"),
            ("search_numero", "search_numero"),
            ("search_operation_nom", "search_operation_nom"),
            ("statuts", "cstatut"),
        ]


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
                departement=loyer_simulateur_form.cleaned_data["departement"],
            )

            annee_validite = loyer_simulateur_form.cleaned_data[
                "date_actualisation"
            ].year

        return render(
            request,
            "conventions/calculette_loyer.html",
            {
                "form": loyer_simulateur_form,
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
            },
        )


@require_POST
@login_required
@currentrole_campaign_permission_required_view_function("convention.change_convention")
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
@currentrole_campaign_permission_required_view_function("convention.delete_convention")
def delete_convention(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    convention.delete()
    return HttpResponseRedirect(reverse("conventions:index"))


@require_POST
@login_required
@currentrole_campaign_permission_required_view_function("convention.change_convention")
def feedback_convention(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.view_convention", convention)
    result = convention_feedback(request, convention)
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


@require_POST
@login_required
@currentrole_campaign_permission_required_view_function(
    "convention.validate_convention"
)
def validate_convention(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("programme__bailleur")
        .prefetch_related("programme__referencecadastrales")
        .prefetch_related("programme__logementedds")
        # .prefetch_related("lot")
        # .prefetch_related("lot__type_stationnements")
        # .prefetch_related("lot__logements")
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
            "convention_form_steps": ConventionFormSteps(
                convention=convention, request=request
            ),
        },
    )


@require_POST
@login_required
@currentrole_campaign_permission_required_view_function("convention.change_convention")
def denonciation_validate(request, convention_uuid):
    convention_denonciation_validate(convention_uuid)
    return HttpResponseRedirect(
        reverse("conventions:post_action", args=[convention_uuid])
    )


@require_POST
@login_required
@currentrole_campaign_permission_required_view_function("convention.change_convention")
def resiliation_validate(request, convention_uuid):
    convention_resiliation_validate(convention_uuid)
    return HttpResponseRedirect(
        reverse("conventions:post_action", args=[convention_uuid])
    )


@login_required
@require_POST
@currentrole_campaign_permission_required_view_function("convention.view_convention")
def get_or_generate_cerfa(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    files_dict = json.loads(convention.fichier_override_cerfa)
    files = list(files_dict["files"].values())
    if len(files) > 0:
        file_dict = files[0]
        uploaded_file = UploadedFile.objects.get(uuid=file_dict["uuid"])
        return FileResponse(
            default_storage.open(
                name=uploaded_file.filepath(convention_uuid),
                mode="rb",
            ),
            filename=(
                file_dict["realname"]
                if "realname" in file_dict
                else file_dict["filename"]
            ),
            as_attachment=True,
        )
    return generate_convention(request, convention_uuid)


@login_required
@require_POST
@currentrole_campaign_permission_required_view_function("convention.view_convention")
def generate_convention(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("programme__bailleur")
        # .prefetch_related("lot")
        # .prefetch_related("lot__type_stationnements")
        # .prefetch_related("lot__logements")
        # .prefetch_related("lot__prets")
        .prefetch_related("programme")
        .prefetch_related("programme__administration")
        .prefetch_related("programme__logementedds")
        .prefetch_related("programme__referencecadastrales")
        .get(uuid=convention_uuid)
    )
    request.user.check_perm("convention.view_convention", convention)

    if request.POST.get("without_filigram"):
        convention.statut = ConventionStatut.A_SIGNER.label

    doc = convention_generator.generate_convention_doc(convention)
    data = io.BytesIO()
    doc.save(data)
    data.seek(0)

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    filename = unidecode(str(convention))
    response["Content-Disposition"] = f"attachment; filename={filename}.docx"
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
        "logements_edd",
        "logements",
        "stationnements",
        "communes",
    ]:
        raise PermissionDenied

    if file_type == "all":
        filepath = (
            settings.BASE_DIR / "static" / "files" / "tous_les_templates_xlsx.zip"
        )
        with ZipFile(filepath, "w") as zip_obj:
            # Add multiple files to the zip
            for each_file in [
                "annexes",
                "cadastre",
                "financement",
                "logements_edd",
                "logements",
                "stationnements",
            ]:
                zip_obj.write(
                    f"{settings.BASE_DIR}/static/files/{each_file}.xlsx",
                    arcname=f"{each_file}.xlsx",
                )
            zip_obj.close()
        with open(filepath, "rb") as zip_file:
            # close the Zip File
            response = HttpResponse(zip_file, content_type="application/force-download")
            zip_file.close()
        response["Content-Disposition"] = (
            'attachment; filename="tous_les_templates_xlsx.zip"'
        )
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
@currentrole_campaign_permission_required_view_function("convention.view_convention")
def preview(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.view_convention", convention)
    return render(
        request,
        "conventions/preview.html",
        {"convention": convention},
    )


# FIXME : to be tested
class ConventionSentView(BaseConventionView):
    @currentrole_campaign_permission_required("convention.view_convention")
    def get(self, request, convention_uuid):
        service = ConventionSentService(convention=self.convention, request=request)
        result = service.get()
        return render(
            request,
            template_sent,
            {
                **result,
            },
        )

    @currentrole_campaign_permission_required("convention.change_convention")
    def post(self, request, convention_uuid):
        service = ConventionSentService(convention=self.convention, request=request)
        result = service.save()
        if result["success"] == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:preview_upload_signed", args=[convention_uuid])
            )

        return render(
            request,
            template_sent,
            {
                **result,
            },
        )


class ConventionBaseUploadSignedView(BaseConventionView):
    step_number: int
    template_path: str

    @currentrole_campaign_permission_required("convention.view_convention")
    def get(self, request, convention_uuid):
        service = ConventionUploadSignedService(
            convention=self.convention, request=request, step_number=self.step_number
        )
        result = service.get()
        return render(
            request,
            self.template_path,
            {
                **result,
            },
        )


class ConventionPreviewUploadSignedView(ConventionBaseUploadSignedView):
    step_number: int = 1
    template_path: str = "conventions/upload_signed/preview_document.html"


class ConventionDateUploadSignedView(ConventionBaseUploadSignedView):
    step_number: int = 2
    template_path: str = "conventions/upload_signed/signature_date.html"

    @currentrole_campaign_permission_required("convention.change_convention")
    def post(self, request, convention_uuid):
        service = ConventionUploadSignedService(
            convention=self.convention, request=request, step_number=2
        )
        result = service.save()
        if result["success"] == ReturnStatus.SUCCESS:
            messages.add_message(
                request,
                messages.SUCCESS,
                service.get_success_message(),
            )
            return HttpResponseRedirect(
                reverse("conventions:post_action", args=[convention_uuid])
            )

        return render(
            request,
            template_sent,
            {
                **result,
            },
        )


class ActionsPostValidation(BaseConventionView):
    @currentrole_campaign_permission_required("convention.view_convention")
    def get(self, request, convention_uuid):
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

    @currentrole_campaign_permission_required("convention.change_convention")
    def post(self, request, convention_uuid):
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
@currentrole_permission_required("convention.add_convention")
def denonciation_start(request, convention_uuid):
    result = create_avenant(request, convention_uuid)

    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:denonciation", args=[result["convention"].uuid])
        )

    return render(
        request,
        "conventions/post_action.html",
        {
            **result,
        },
    )


@login_required
@currentrole_permission_required("convention.add_convention")
def resiliation_start(request, convention_uuid):
    result = create_avenant(request, convention_uuid)

    if result["success"] == ReturnStatus.SUCCESS:
        if request.user.is_instructeur_departemental():
            return HttpResponseRedirect(
                reverse("conventions:resiliation", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse(
                "conventions:resiliation_creation", args=[result["convention"].uuid]
            )
        )

    return render(
        request,
        "conventions/post_action.html",
        {
            **result,
        },
    )


@login_required
@currentrole_campaign_permission_required_view_function("convention.view_convention")
def display_pdf(request, convention_uuid):
    # récupérer le doc PDF
    convention = Convention.objects.get(uuid=convention_uuid)
    convention_path = f"conventions/{convention.uuid}/convention_docs"

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
        and default_storage.exists(f"{convention_path}/{convention.nom_fichier_signe}")
    ):
        filename = convention.nom_fichier_signe
    elif default_storage.exists(f"{convention_path}/{convention.uuid}.pdf"):
        filename = f"{convention.uuid}.pdf"
    elif default_storage.exists(f"{convention_path}/{convention.uuid}.docx"):
        filename = f"{convention.uuid}.docx"

    if filename:
        return FileResponse(
            default_storage.open(
                name=f"{convention_path}/{filename}",
                mode="rb",
            ),
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
                    **utils.get_text_and_files_from_field(
                        "pieces_jointes",
                        selected.pieces_jointes,
                    ),
                )
            )
        # Handle submitted data
        if action == "submit":
            form = EvenementForm(
                {
                    "uuid": request.POST.get("uuid"),
                    "description": request.POST.get("description"),
                    "type_evenement": request.POST.get("type_evenement"),
                    **utils.init_text_and_files_from_field(
                        request, None, "pieces_jointes"
                    ),
                }
            )
            if form.is_valid():
                if form.cleaned_data["uuid"] is not None:
                    evenement = Evenement.objects.get(uuid=form.cleaned_data["uuid"])
                    evenement.description = form.cleaned_data["description"]
                    evenement.type_evenement = form.cleaned_data["type_evenement"]
                    evenement.pieces_jointes = utils.set_files_and_text_field(
                        form.cleaned_data["pieces_jointes_files"],
                        form.cleaned_data["pieces_jointes"],
                    )
                    evenement.save()
                else:
                    evenement = Evenement.objects.create(
                        convention=convention,
                        description=form.cleaned_data["description"],
                        type_evenement=form.cleaned_data["type_evenement"],
                    )
                    evenement.pieces_jointes = utils.set_files_and_text_field(
                        form.cleaned_data["pieces_jointes_files"],
                        form.cleaned_data["pieces_jointes"],
                    )
                    evenement.save()

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
@currentrole_campaign_permission_required_view_function("convention.view_convention")
def fiche_caf(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        # .prefetch_related("lot__logements")
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
@currentrole_permission_required("convention.add_convention")
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
@currentrole_permission_required("convention.add_convention")
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
@currentrole_permission_required("convention.change_convention")
def expert_mode(request, convention_uuid):
    request.session["is_expert"] = not request.session.get("is_expert")
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[convention_uuid])
    )
