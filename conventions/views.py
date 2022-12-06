from abc import ABC

from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_GET, require_http_methods

from upload.services import UploadService
from conventions.models import Convention, ConventionStatut
from conventions.permissions import has_campaign_permission
from conventions.services.convention_generator import fiche_caf_doc
from conventions.services.services_bailleurs import ConventionBailleurService
from conventions.services.services_conventions import (
    ConventionCommentsService,
    ConventionFinancementService,
    ConventionService,
    convention_delete,
    convention_feedback,
    convention_post_action,
    convention_preview,
    convention_sent,
    convention_submit,
    convention_summary,
    convention_validate,
    conventions_index,
    create_avenant,
    generate_convention_service,
)
from conventions.services.services_logements import (
    ConventionAnnexesService,
    ConventionLogementsService,
    ConventionTypeStationnementService,
)
from conventions.services.services_programmes import (
    ConventionProgrammeService,
    ConventionEDDService,
    ConventionCadastreService,
    ConventionSelectionService,
)
from conventions.services.utils import (
    base_convention_response_error,
    editable_convention,
    ReturnStatus,
)


@login_required
def index(request):
    result = conventions_index(request)
    return render(
        request,
        "conventions/index.html",
        {**result},
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
        {
            **result,
        },
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
        "annexes",
        "cadastre",
        "financement",
        "logements_edd",
        "logements",
        "listing_bailleur",
        "stationnements",
        "all",
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
@permission_required("convention.add_convention")
def new_avenant(request, convention_uuid):
    result = create_avenant(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result["avenant_type"].nom == "logements":
            return HttpResponseRedirect(
                reverse(
                    "conventions:avenant_logements", args=[result["convention"].uuid]
                )
            )
        if result["avenant_type"].nom == "bailleur":
            return HttpResponseRedirect(
                reverse(
                    "conventions:avenant_bailleur", args=[result["convention"].uuid]
                )
            )
        if result["avenant_type"].nom == "duree":
            return HttpResponseRedirect(
                reverse(
                    "conventions:avenant_financement", args=[result["convention"].uuid]
                )
            )
        if result["avenant_type"].nom == "commentaires":
            return HttpResponseRedirect(
                reverse(
                    "conventions:avenant_comments", args=[result["convention"].uuid]
                )
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
    current_path_redirect: None | str = None
    next_path_redirect: str
    service_class: ConventionService
    form_step: None | dict

    def _get_convention(self, convention_uuid):
        return Convention.objects.get(uuid=convention_uuid)

    def _get_form_steps(self):
        if self.form_step:
            return {
                "form_step": self.form_step | {"next_target": self.next_path_redirect}
            }
        return {}

    @has_campaign_permission("convention.view_convention")
    def get(self, request, convention_uuid):
        convention = self._get_convention(convention_uuid)
        service = self.service_class(convention=convention, request=request)
        service.get()
        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                **self._get_form_steps(),
                "editable_after_upload": (
                    editable_convention(request, convention)
                    or service.editable_after_upload
                ),
            },
        )

    @has_campaign_permission("convention.change_convention")
    def post(self, request, convention_uuid):
        convention = self._get_convention(convention_uuid)
        service = self.service_class(convention=convention, request=request)
        service.save()
        if service.return_status == ReturnStatus.SUCCESS:
            if service.redirect_recap:
                return HttpResponseRedirect(
                    reverse("conventions:recapitulatif", args=[convention.uuid])
                )
            return HttpResponseRedirect(
                reverse(self.next_path_redirect, args=[convention.uuid])
            )
        if service.return_status == ReturnStatus.REFRESH:
            return HttpResponseRedirect(
                reverse(self.current_path_redirect, args=[convention.uuid])
            )
        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                **self._get_form_steps(),
                **(
                    {"import_warnings": service.import_warnings}
                    if service.import_warnings
                    else {}
                ),
                "editable_after_upload": editable_convention(request, convention)
                or service.editable_after_upload,
            },
        )


class ConventionSelectionFromDBView(LoginRequiredMixin, View):

    # @permission_required("convention.add_convention")
    def get(self, request):

        service = ConventionSelectionService(request)
        service.get_from_db()

        return render(
            request,
            "conventions/selection_from_db.html",
            {
                "form": service.form,
                "lots": service.lots,
                "editable": True,
            },
        )

    # @permission_required("convention.add_convention")
    def post(self, request):
        service = ConventionSelectionService(request)
        service.post_from_db()

        if service.return_status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[service.convention.uuid])
            )
        return render(
            request,
            "conventions/selection_from_db.html",
            {
                "form": service.form,
                "lots": service.lots,
                "editable": True,
            },
        )


class ConventionSelectionFromZeroView(LoginRequiredMixin, View):

    # @permission_required("convention.add_convention")
    def get(self, request):
        service = ConventionSelectionService(request)
        service.get_from_zero()

        return render(
            request,
            "conventions/selection_from_zero.html",
            {
                "form": service.form,
                "editable": True,
            },
        )

    # @permission_required("convention.add_convention")
    def post(self, request):
        service = ConventionSelectionService(request)
        service.post_from_zero()

        if service.return_status == ReturnStatus.SUCCESS:
            return HttpResponseRedirect(
                reverse("conventions:bailleur", args=[service.convention.uuid])
            )
        return render(
            request,
            "conventions/selection_from_zero.html",
            {
                "form": service.form,
                "editable": True,
            },
        )


class ConventionBailleurView(ConventionView):
    target_template: str = "conventions/bailleur.html"
    next_path_redirect: str = "conventions:programme"
    current_path_redirect: str = "conventions:bailleur"
    service_class = ConventionBailleurService
    form_step: dict = {
        "number": 1,
        "total": 9,
        "title": "Bailleur",
        "next": "Opération",
    }


class AvenantBailleurView(ConventionBailleurView):
    next_path_redirect: str = "conventions:recapitulatif"
    current_path_redirect: str = "conventions:avenant_bailleur"
    form_step = {}


class ConventionProgrammeView(ConventionView):
    target_template: str = "conventions/programme.html"
    next_path_redirect: str = "conventions:cadastre"
    service_class = ConventionProgrammeService
    form_step: dict = {
        "number": 2,
        "total": 9,
        "title": "Opération",
        "next": "Cadastre",
    }

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("lot")
            .get(uuid=convention_uuid)
        )


class ConventionCadastreView(ConventionView):
    target_template: str = "conventions/cadastre.html"
    next_path_redirect: str = "conventions:edd"
    service_class = ConventionCadastreService
    form_step: dict = {
        "number": 3,
        "total": 9,
        "title": "Cadastre",
        "next": "EDD",
    }

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("programme__referencecadastrales")
            .get(uuid=convention_uuid)
        )


class ConventionEDDView(ConventionView):
    target_template: str = "conventions/edd.html"
    next_path_redirect: str = "conventions:financement"
    service_class = ConventionEDDService
    form_step: dict = {
        "number": 4,
        "total": 9,
        "title": "EDD",
        "next": "Financement",
    }

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("lot")
            .prefetch_related("programme__logementedds")
            .get(uuid=convention_uuid)
        )


class ConventionFinancementView(ConventionView):
    target_template: str = "conventions/financement.html"
    next_path_redirect: str = "conventions:logements"
    service_class = ConventionFinancementService
    form_step: dict = {
        "number": 5,
        "total": 9,
        "title": "Financement",
        "next": "Logements",
    }

    def _get_convention(self, convention_uuid):
        return Convention.objects.prefetch_related("prets").get(uuid=convention_uuid)


class AvenantFinancementView(ConventionFinancementView):
    target_template: str = "conventions/financement.html"
    next_path_redirect: str = "conventions:recapitulatif"
    service_class = ConventionFinancementService
    form_step = {}


class ConventionLogementsView(ConventionView):
    target_template: str = "conventions/logements.html"
    next_path_redirect: str = "conventions:annexes"
    service_class = ConventionLogementsService
    form_step: dict = {
        "number": 6,
        "total": 9,
        "title": "Logements",
        "next": "Annexes",
    }

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements")
            .get(uuid=convention_uuid)
        )


class AvenantLogementsView(ConventionLogementsView):
    target_template: str = "conventions/logements.html"
    next_path_redirect: str = "conventions:avenant_annexes"
    service_class = ConventionLogementsService
    form_step: dict = {
        "number": 1,
        "total": 2,
        "title": "Logements",
        "next": "Annexes",
    }


class ConventionAnnexesView(ConventionView):
    target_template: str = "conventions/annexes.html"
    next_path_redirect: str = "conventions:stationnements"
    service_class = ConventionAnnexesService
    form_step: dict = {
        "number": 7,
        "total": 9,
        "title": "Annexes",
        "next": "Stationnements",
    }

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements__annexes")
            .get(uuid=convention_uuid)
        )


class AvenantAnnexesView(ConventionAnnexesView):
    next_path_redirect: str = "conventions:recapitulatif"
    service_class = ConventionAnnexesService
    form_step: dict = {
        "number": 2,
        "total": 2,
        "title": "Annexes",
        "next": "Recapitulatif",
    }


class ConventionTypeStationnementView(ConventionView):
    target_template: str = "conventions/stationnements.html"
    next_path_redirect: str = "conventions:comments"
    service_class = ConventionTypeStationnementService
    form_step: dict = {
        "number": 8,
        "total": 9,
        "title": "Stationnements",
        "next": "Commentaires",
    }


class ConventionCommentsView(ConventionView):
    target_template: str = "conventions/comments.html"
    next_path_redirect: str = "conventions:recapitulatif"
    service_class = ConventionCommentsService
    form_step: dict = {
        "number": 9,
        "total": 9,
        "title": "Commentaires",
        "next": "Récapitulatif",
    }


class AvenantCommentsView(ConventionCommentsView):
    next_path_redirect: str = "conventions:recapitulatif"
    form_step: dict = {}
