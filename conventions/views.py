from zipfile import ZipFile

from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_GET, require_http_methods
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from programmes.models import FinancementEDD
from conventions.models import Convention
from conventions.services import services, convention_generator
from conventions.services.utils import ReturnStatus
from upload.services import UploadService


@login_required
def index(request):
    result = services.conventions_index(request)
    return render(
        request,
        "conventions/index.html",
        {**result},
    )


@login_required
@permission_required("convention.add_convention")
def select_programme_create(request):
    # STEP 1
    result = services.select_programme_create(request)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:bailleur", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/selection.html",
        {
            **result,
            # Force Financment to EDD Financement because PLUS-PLAI doesn't exist
            "financements": FinancementEDD,
        },
    )


@login_required
def bailleur(request, convention_uuid):
    # STEP 2
    result = services.bailleur_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:programme", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/bailleur.html",
        {
            **result,
            "convention_form_step": 1,
        },
    )


@login_required
def programme(request, convention_uuid):
    # STEP 3
    result = services.programme_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:cadastre", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/programme.html",
        {
            **result,
            "convention_form_step": 2,
        },
    )


@login_required
def cadastre(request, convention_uuid):
    # STEP 4
    result = services.programme_cadastral_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:edd", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/cadastre.html",
        {
            **result,
            "convention_form_step": 3,
        },
    )


@login_required
def edd(request, convention_uuid):
    # STEP 5
    result = services.programme_edd_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:financement", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/edd.html",
        {
            **result,
            "convention_form_step": 4,
        },
    )


@login_required
def financement(request, convention_uuid):
    result = services.convention_financement(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:logements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/financement.html",
        {
            **result,
            "convention_form_step": 5,
            "years": range(2021, 2121),
        },
    )


@login_required
def logements(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:annexes", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/logements.html",
        {
            **result,
            "convention_form_step": 6,
        },
    )


@login_required
def avenant_logements(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse(
                    "conventions:avenant_recapitulatif",
                    args=[result["convention"].uuid],
                )
            )
        return HttpResponseRedirect(
            reverse("conventions:avenant_annexes", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/avenant_logements.html",
        {
            **result,
            "convention_form_step": 60,
        },
    )


@login_required
def annexes(request, convention_uuid):
    result = services.annexes_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:stationnements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/annexes.html",
        {
            **result,
            "convention_form_step": 7,
        },
    )


@login_required
def avenant_annexes(request, convention_uuid):
    result = services.annexes_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse(
                    "conventions:avenant_recapitulatif",
                    args=[result["convention"].uuid],
                )
            )
        return HttpResponseRedirect(
            reverse("conventions:avenant_comments", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/avenant_annexes.html",
        {
            **result,
            "convention_form_step": 70,
        },
    )


@login_required
def stationnements(request, convention_uuid):
    result = services.stationnements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:comments", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/stationnements.html",
        {
            **result,
            "convention_form_step": 8,
        },
    )


@login_required
def comments(request, convention_uuid):
    result = services.convention_comments(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/comments.html",
        {
            **result,
            "convention_form_step": 9,
        },
    )


@login_required
def avenant_comments(request, convention_uuid):
    result = services.convention_comments(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse(
                    "conventions:avenant_recapitulatif",
                    args=[result["convention"].uuid],
                )
            )
        return HttpResponseRedirect(
            reverse(
                "conventions:avenant_recapitulatif", args=[result["convention"].uuid]
            )
        )
    return render(
        request,
        "conventions/avenant_comments.html",
        {
            **result,
            "convention_form_step": 90,
        },
    )


@login_required
def recapitulatif(request, convention_uuid):
    # Step 11/11
    result = services.convention_summary(request, convention_uuid)
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
            "convention_form_step": 10,
        },
    )


@login_required
def avenant_recapitulatif(request, convention_uuid):
    # Step 11/11
    result = services.convention_summary(request, convention_uuid)
    return render(
        request,
        "conventions/avenant_recapitulatif.html",
        {
            **result,
            "convention_form_step": 100,
        },
    )


@login_required
def save_convention(request, convention_uuid):
    result = services.convention_submit(request, convention_uuid)
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
    services.convention_delete(request, convention_uuid)
    return HttpResponseRedirect(reverse("conventions:index"))


@login_required
def feedback_convention(request, convention_uuid):
    result = services.convention_feedback(request, convention_uuid)
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


@login_required
def validate_convention(request, convention_uuid):
    result = services.convention_validate(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
            "convention_form_step": 10,
        },
    )


@login_required
def generate_convention(request, convention_uuid):
    data, file_name = services.generate_convention(request, convention_uuid)

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename={file_name}.docx"
    return response


@login_required
def load_xlsx_model(request, file_type):
    if file_type not in [
        "annexes",
        "cadastre",
        "financement",
        "logements_edd",
        "logements",
        "stationnements",
        "all",
    ]:
        raise PermissionDenied

    if file_type == "all":
        filepath = f"{settings.BASE_DIR}/static/files/tous_les_templates_xlsx.zip"
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

    filepath = f"{settings.BASE_DIR}/static/files/{file_type}.xlsx"

    with open(filepath, "rb") as excel:
        data = excel.read()

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename={file_type}.xlsx"
    return response


@login_required
def display_operation(request, programme_uuid, programme_financement):
    result = services.display_operation(request, programme_uuid, programme_financement)
    if result["success"] == ReturnStatus.SUCCESS and result["convention"]:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    if result["success"] == ReturnStatus.WARNING:
        return render(
            request,
            "conventions/selection.html",
            {
                **result,
                "financements": FinancementEDD,
                "redirect_action": "/conventions/selection",
            },
        )
    return PermissionDenied


@login_required
def preview(request, convention_uuid):
    # Step 11/12
    result = services.convention_preview(convention_uuid)
    filepath = f"{settings.BASE_DIR}"
    return render(
        request,
        "conventions/preview.html",
        {
            **result,
            "filepath": filepath,
            "convention_form_step": 11,
        },
    )


@login_required
def sent(request, convention_uuid):
    # Step 12/12
    result = services.convention_sent(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:preview", args=[convention_uuid])
        )
    return render(
        request,
        "conventions/sent.html",
        {
            **result,
            "convention_form_step": 12,
        },
    )


@require_http_methods(["GET", "POST"])
def post_action(request, convention_uuid):
    # Step 12/12
    result = services.convention_post_action(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[convention_uuid])
        )
    return render(
        request,
        "conventions/post_action.html",
        {
            **result,
            "convention_form_step": 12,
        },
    )


@login_required
def display_pdf(request, convention_uuid):
    # récupérer le doc PDF
    convention = Convention.objects.get(uuid=convention_uuid)
    if convention.nom_fichier_signe:
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

    raise Http404


@login_required
@require_GET
def fiche_caf(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("bailleur")
        .prefetch_related("lot")
        .prefetch_related("lot__logements")
        .prefetch_related("programme")
        .prefetch_related("programme__administration")
        .get(uuid=convention_uuid)
    )
    file_stream = convention_generator.fiche_caf_doc(convention)

    #    return file_stream, f"{convention}"

    #   data, file_name = services.fiche_caf(request, convention_uuid)

    response = HttpResponse(
        file_stream,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename=ficheCAF_{convention}.docx"
    return response


@login_required
@permission_required("convention.add_convention")
def new_avenant(request, convention_uuid):
    result = services.create_avenant(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:avenant_logements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/new_avenant.html",
        {
            **result,
        },
    )
