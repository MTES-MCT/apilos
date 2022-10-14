from abc import ABC

from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_GET, require_http_methods
from bailleurs.models import Bailleur

from programmes.models import FinancementEDD
from programmes.services import programme_change_bailleur
from upload.services import UploadService
from conventions.models import Convention
from conventions.permissions import has_campaign_permission
from conventions.services import convention_generator, services, utils
from conventions.services.services_programmes import ConventionProgrammeService
from conventions.services.services_bailleurs import ConventionBailleurService
from conventions.services.services_conventions import (
    ConventionCommentsService,
    ConventionService,
)
from conventions.services.services_logements import ConventionTypeStationnementService
from conventions.services.utils import ReturnStatus


@login_required
def index(request):
    result = services.conventions_index(request)
    return render(
        request,
        "conventions/index.html",
        {**result},
    )


def change_bailleur(request, convention_uuid):
    convention = Convention.objects.prefetch_related("programme").get(
        uuid=convention_uuid
    )
    bailleur = Bailleur.objects.get(uuid=request.POST["bailleur"])
    programme_change_bailleur(convention.programme, bailleur)

    return HttpResponseRedirect(reverse("conventions:bailleur", args=[convention_uuid]))


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
            # Force Financement to EDD Financement because PLUS-PLAI doesn't exist
            "financements": FinancementEDD,
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
            "form_step": {
                "number": 3,
                "total": 9,
                "title": "Cadastre",
                "next": "EDD",
                "next_target": "conventions:edd",
            },
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
            "form_step": {
                "number": 4,
                "total": 9,
                "title": "EDD",
                "next": "Financement",
                "next_target": "conventions:financement",
            },
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
            "years": range(2021, 2121),
            "form_step": {
                "number": 5,
                "total": 9,
                "title": "Financement",
                "next": "Logements",
                "next_target": "conventions:logements",
            },
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
            "form_step": {
                "number": 6,
                "total": 9,
                "title": "Logements",
                "next": "Annexes",
                "next_target": "conventions:annexes",
            },
        },
    )


@login_required
def avenant_logements(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse(
                    "conventions:recapitulatif",
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
            "form_step": {
                "number": 1,
                "total": 4,
                "title": "Logements",
                "next": "Annexes",
                "next_target": "conventions:avenant_annexes",
            },
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
            "form_step": {
                "number": 7,
                "total": 9,
                "title": "Annexes",
                "next": "Stationnements",
                "next_target": "conventions:stationnements",
            },
        },
    )


@login_required
def avenant_annexes(request, convention_uuid):
    result = services.annexes_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse(
                    "conventions:recapitulatif",
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
            "form_step": {
                "number": 2,
                "total": 4,
                "title": "Annexes",
                "next": "Commentaires",
                "next_target": "conventions:avenant_comments",
            },
        },
    )


@login_required
def recapitulatif(request, convention_uuid):
    # Step 11/11
    result = services.convention_summary(request, convention_uuid)
    if result["convention"].is_avenant():
        return render(
            request,
            "conventions/avenant_recapitulatif.html",
            {
                **result,
                "form_step": {
                    "number": 4,
                    "total": 4,
                    "title": "Récapitulatif",
                },
            },
        )
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
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


# @login_required
# def display_operation(request, programme_uuid, programme_financement):
#     result = services.display_operation(request, programme_uuid, programme_financement)
#     if result["success"] == ReturnStatus.SUCCESS and result["convention"]:
#         return HttpResponseRedirect(
#             reverse("conventions:recapitulatif", args=[result["convention"].uuid])
#         )
#     if result["success"] == ReturnStatus.WARNING:
#         return render(
#             request,
#             "conventions/selection.html",
#             {
#                 **result,
#                 "financements": FinancementEDD,
#                 "redirect_action": "/conventions/selection",
#             },
#         )
#     return PermissionDenied


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
        },
    )


@login_required
def display_pdf(request, convention_uuid):
    # récupérer le doc PDF
    convention = Convention.objects.get(uuid=convention_uuid)
    filename = None
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


class ConventionView(ABC, LoginRequiredMixin, View):

    target_template: str
    next_path_redirect: str
    service_class: ConventionService
    form_step: None | dict

    def _get_convention(self, convention_uuid):
        return Convention.objects.get(uuid=convention_uuid)

    @has_campaign_permission("convention.view_convention")
    def get(self, request, convention_uuid):
        convention = self._get_convention(convention_uuid)
        service = self.service_class(convention=convention, request=request)
        service.get()
        return render(
            request,
            self.target_template,
            {
                **utils.base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                **({"form_step": self.form_step} if self.form_step else {}),
                "editable_after_upload": (
                    utils.editable_convention(request, convention)
                    or service.editable_after_upload
                ),
            },
        )

    @has_campaign_permission("convention.change_convention")
    def post(self, request, convention_uuid):
        convention = self._get_convention(convention_uuid)
        service = self.service_class(convention=convention, request=request)
        service.save()
        if service.return_status == utils.ReturnStatus.SUCCESS:
            if service.redirect_recap:
                return HttpResponseRedirect(
                    reverse("conventions:recapitulatif", args=[convention.uuid])
                )
            return HttpResponseRedirect(
                reverse(self.next_path_redirect, args=[convention.uuid])
            )
        return render(
            request,
            self.target_template,
            {
                **utils.base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                **({"form_step": self.form_step} if self.form_step else {}),
                **(
                    {"import_warnings": service.import_warnings}
                    if service.import_warnings
                    else {}
                ),
                "editable_after_upload": utils.editable_convention(request, convention)
                or service.editable_after_upload,
            },
        )


class ConventionBailleurView(ConventionView):
    target_template: str = "conventions/bailleur.html"
    next_path_redirect: str = "conventions:programme"
    service_class = ConventionBailleurService
    form_step: dict = {
        "number": 1,
        "total": 9,
        "title": "Bailleur",
        "next": "Opération",
        "next_target": next_path_redirect,
    }

    def _get_convention(self, convention_uuid):
        return Convention.objects.prefetch_related("bailleur").get(uuid=convention_uuid)


class ConventionProgrammeView(ConventionView):
    target_template: str = "conventions/programme.html"
    next_path_redirect: str = "conventions:cadastre"
    service_class = ConventionProgrammeService
    form_step: dict = {
        "number": 2,
        "total": 9,
        "title": "Opération",
        "next": "Cadastre",
        "next_target": next_path_redirect,
    }

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("lot")
            .get(uuid=convention_uuid)
        )


class ConventionTypeStationnementView(ConventionView):
    target_template: str = "conventions/stationnements.html"
    next_path_redirect: str = "conventions:comments"
    service_class: ConventionService = ConventionTypeStationnementService
    form_step: dict = {
        "number": 8,
        "total": 9,
        "title": "Stationnements",
        "next": "Commentaires",
        "next_target": next_path_redirect,
    }


class ConventionCommentsView(ConventionView):
    target_template: str = "conventions/comments.html"
    next_path_redirect: str = "conventions:recapitulatif"
    service_class: ConventionService = ConventionCommentsService
    form_step: dict = {
        "number": 9,
        "total": 9,
        "title": "Commentaires",
        "next": "Récapitulatif",
        "next_target": next_path_redirect,
    }


class AvenantCommentsView(ConventionCommentsView):

    target_template: str = "conventions/avenant_comments.html"
    next_path_redirect: str = "conventions:recapitulatif"
    form_step: dict = {
        "number": 3,
        "total": 4,
        "title": "Commentaires",
        "next": "Récapitulatif",
        "next_target": next_path_redirect,
    }
