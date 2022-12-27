from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from core.storage import client
from programmes.models import Financement
from upload.services import UploadService
from conventions.services.file import ConventionFileService
from conventions.views.convention_form import ConventionFormSteps
from conventions.models import Convention, ConventionStatut, PieceJointe
from conventions.services.convention_generator import fiche_caf_doc
from conventions.services.services_conventions import (
    convention_delete,
    convention_feedback,
    convention_post_action,
    convention_preview,
    convention_sent,
    convention_submit,
    convention_summary,
    convention_validate,
    generate_convention_service,
    ConventionListService,
)


from conventions.services.utils import (
    ReturnStatus,
)


@login_required
@require_GET
def search(request, active: bool = True):
    query_set = request.user.conventions(active=active)

    service = ConventionListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "programme__date_achevement_compile"),
        page=request.GET.get("page", 1),
        statut_filter=request.GET.get("cstatut", ""),
        financement_filter=request.GET.get("financement", ""),
        departement_input=request.GET.get("departement_input", ""),
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
        },
    )


@login_required
def recapitulatif(request, convention_uuid):
    # Step 11/11
    convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("programme__referencecadastrales")
        .prefetch_related("programme__logementedds")
        .prefetch_related("lot")
        .prefetch_related("lot__type_stationnements")
        .prefetch_related("lot__logements")
        .prefetch_related("programme__administration")
        .get(uuid=convention_uuid)
    )
    result = convention_summary(request, convention)
    if convention.is_avenant():
        result["avenant_list"] = [
            avenant_type.nom for avenant_type in convention.avenant_types.all()
        ]

    return render(
        request,
        "conventions/recapitulatif.html",
        {**result, "convention_form_steps": ConventionFormSteps(convention=convention)},
    )


@login_required
def save_convention(request, convention_uuid):
    result = convention_submit(request, convention_uuid)
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
def delete_convention(request, convention_uuid):
    convention_delete(request, convention_uuid)
    return HttpResponseRedirect(reverse("conventions:index"))


@login_required
def feedback_convention(request, convention_uuid):
    result = convention_feedback(request, convention_uuid)
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


@login_required
def validate_convention(request, convention_uuid):
    result = convention_validate(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:sent", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
        },
    )


@login_required
def generate_convention(request, convention_uuid):
    data, file_name = generate_convention_service(request, convention_uuid)

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename={file_name}.docx"
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


@login_required
def preview(request, convention_uuid):
    result = convention_preview(convention_uuid)
    return render(
        request,
        "conventions/preview.html",
        result,
    )


@login_required
def sent(request, convention_uuid):
    # Step 12/12
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


@require_http_methods(["GET", "POST"])
def post_action(request, convention_uuid):
    # Step 12/12
    result = convention_post_action(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[convention_uuid])
        )
    return render(
        request,
        "conventions/post_action.html",
        {
            **result,
        },
    )


@login_required
def display_pdf(request, convention_uuid):
    # récupérer le doc PDF
    convention = Convention.objects.get(uuid=convention_uuid)
    filename = None
    if (
        convention.statut
        in [
            ConventionStatut.SIGNEE,
            ConventionStatut.RESILIEE,
            ConventionStatut.DENONCEE,
            ConventionStatut.ANNULEE,
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


@login_required
@require_GET
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
    s3_object = client.get_object(
        settings.AWS_ECOLOWEB_BUCKET_NAME,
        f"piecesJointes/{piece_jointe_from_db.fichier}",
    )

    if s3_object is None:
        return HttpResponseNotFound()
    return FileResponse(
        s3_object["Body"],
        filename=piece_jointe_from_db.nom_reel,
        content_type=s3_object["ContentType"],
    )


@login_required
@permission_required("convention.add_convention")
def piece_jointe_promote(piece_jointe_uuid):
    """
    Promote a pièce jointe to the official PDF document of a convention
    """
    piece_jointe = PieceJointe.objects.get(uuid=piece_jointe_uuid)

    if piece_jointe is None:
        return HttpResponseNotFound

    if piece_jointe.convention.ecolo_reference is None:
        return HttpResponseForbidden()

    if not piece_jointe.is_convention():
        return HttpResponseForbidden()

    if not ConventionFileService.promote_piece_jointe(piece_jointe):
        return HttpResponseNotFound

    return HttpResponseRedirect(
        reverse("conventions:preview", args=[piece_jointe.convention.uuid])
    )
