import mimetypes
from datetime import date
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.storage import default_storage
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from bailleurs.models import Bailleur
from conventions.forms.convention_form_simulateur_loyer import LoyerSimulateurForm
from conventions.models import Convention, ConventionStatut, PieceJointe
from conventions.permissions import (
    has_campaign_permission,
    has_campaign_permission_view_function,
)
from conventions.services import convention_generator
from conventions.services.convention_generator import fiche_caf_doc
from conventions.services.conventions import (
    convention_post_action,
    convention_sent,
    ConventionListService,
)
from conventions.services.file import ConventionFileService
from conventions.services.recapitulatif import (
    ConventionRecapitulatifService,
    convention_feedback,
    convention_submit,
    convention_validate,
)
from conventions.services.utils import ReturnStatus, base_convention_response_error
from conventions.views.convention_form import BaseConventionView, ConventionFormSteps
from core.storage import client
from core.utils import is_valid_uuid
from instructeurs.models import Administration
from programmes.models import Financement, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer
from upload.services import UploadService


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
    def post(self, request: HttpRequest, convention_uuid: int):
        # pylint: disable=unused-argument
        service = ConventionRecapitulatifService(
            request=request, convention=self.convention
        )

        if request.POST.get("update_programme_number"):
            result = service.update_programme_number()
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


@login_required
@require_GET
def search(request, active: bool = True):
    query_set = request.user.conventions(active=active)
    uuid_bailleur = request.GET.get("bailleur")
    bailleur = (
        Bailleur.objects.filter(uuid=uuid_bailleur).first()
        if is_valid_uuid(uuid_bailleur)
        else None
    )
    bailleur_query = (
        request.user.bailleurs(full_scope=True).exclude(nom__exact="")[
            : settings.APILOS_MAX_DROPDOWN_COUNT
        ]
        if request.user.is_instructeur()
        else None
    )

    uuid_administration = request.GET.get("administration")
    administration = (
        Administration.objects.filter(uuid=uuid_administration).first()
        if is_valid_uuid(uuid_administration)
        else None
    )
    administration_query = (
        request.user.administrations()[: settings.APILOS_MAX_DROPDOWN_COUNT]
        if request.user.is_bailleur()
        else None
    )

    service = ConventionListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get(
            "order_by",
            "programme__date_achevement_compile"
            if active
            else "televersement_convention_signee_le",
        ),
        active=active,
        page=request.GET.get("page", 1),
        statut_filter=request.GET.get("cstatut", ""),
        financement_filter=request.GET.get("financement", ""),
        departement_input=request.GET.get("departement_input", ""),
        ville=request.GET.get("ville"),
        anru=(request.GET.get("anru") is not None),  # As anru is a checkbox
        user=request.user,
        bailleur=bailleur,
        administration=administration,
        my_convention_list=query_set.prefetch_related("programme")
        .prefetch_related("programme__administration")
        .prefetch_related("lot"),
    )
    service.paginate()

    return render(
        request,
        "conventions/index.html",
        {
            "active": active,
            "statuts": ConventionStatut,
            "financements": Financement,
            "nb_active_conventions": request.user.conventions(active=True).count(),
            "nb_completed_conventions": request.user.conventions(active=False).count(),
            "conventions": service,
            "bailleur_query": bailleur_query,
            "administration_query": administration_query,
        },
    )


@login_required
def loyer_simulateur(request):
    annee_validite = None
    montant_actualise = None

    if request.method == "POST":
        loyer_simulateur_form = LoyerSimulateurForm(request.POST)

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
    else:
        loyer_simulateur_form = LoyerSimulateurForm(
            initial=dict(
                date_actualisation=date.today().isoformat(),
                nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            )
        )

    return render(
        request,
        "conventions/loyer.html",
        {
            "form": loyer_simulateur_form,
            "montant_actualise": montant_actualise,
            "annee_validite": annee_validite,
            "nb_active_conventions": request.user.conventions(active=True).count(),
            "nb_completed_conventions": request.user.conventions(active=False).count(),
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
    if result["success"] == ReturnStatus.SUCCESS:
        return render(
            request,
            "conventions/submitted.html",
            result,
        )
    if result["success"] == ReturnStatus.WARNING:
        return render(
            request,
            "conventions/saved.html",
            result,
        )
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


@login_required
@has_campaign_permission_view_function("convention.delete_convention")
def delete_convention(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.change_convention", convention)
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


@require_GET
@login_required
def journal(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    return render(
        request,
        "conventions/journal.html",
        {"convention": convention},
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
