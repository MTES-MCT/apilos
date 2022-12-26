from abc import ABC
from datetime import datetime
from typing import List

from zipfile import ZipFile
from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_GET, require_http_methods

from core.storage import client
from programmes.models import Financement
from upload.services import UploadService
from conventions.models import Convention, ConventionStatut, PieceJointe
from conventions.permissions import has_campaign_permission
from conventions.services.variantes import ConventionFoyerVariantesService
from conventions.services.attribution import ConventionFoyerAttributionService
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
    generate_convention_service,
    ConventionListService,
)
from conventions.services.collectif import ConventionCollectifService


from conventions.services.services_logements import (
    ConventionAnnexesService,
    ConventionFoyerResidenceLogementsService,
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
@permission_required("convention.add_convention")
def piece_jointe(request, piece_jointe_uuid):
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
def piece_jointe_promote(request, piece_jointe_uuid):
    """
    Promote a pièce jointe to the official PDF document of a convention
    """
    piece_jointe_from_db = PieceJointe.objects.get(uuid=piece_jointe_uuid)

    if piece_jointe_from_db is None:
        return HttpResponseNotFound

    if piece_jointe_from_db.convention.ecolo_reference is None:
        return HttpResponseForbidden()

    if not piece_jointe_from_db.is_convention():
        return HttpResponseForbidden()

    o = client.get_object(
        settings.AWS_ECOLOWEB_BUCKET_NAME,
        f"piecesJointes/{piece_jointe_from_db.fichier}",
    )

    if o is None:
        return HttpResponseNotFound

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{now}_convention_{piece_jointe_from_db.convention.uuid}_signed.pdf"
    upload_service = UploadService(
        convention_dirpath=f"conventions/{piece_jointe_from_db.convention.uuid}/convention_docs",
        filename=filename,
    )
    upload_service.upload_file(o["Body"])

    piece_jointe_from_db.convention.statut = ConventionStatut.SIGNEE
    piece_jointe_from_db.convention.nom_fichier_signe = filename
    piece_jointe_from_db.convention.televersement_convention_signee_le = timezone.now()
    piece_jointe_from_db.convention.save()

    return HttpResponseRedirect(
        reverse("conventions:preview", args=[piece_jointe_from_db.convention.uuid])
    )


@dataclass
class ConventionFormStep:
    pathname: str  # "convention:programme"
    label: str
    classname: str | None


bailleur_step = ConventionFormStep(
    pathname="conventions:bailleur",
    label="Bailleur",
    classname="ConventionBailleurView",
)

programme_step = ConventionFormStep(
    pathname="conventions:programme",
    label="Opération",
    classname="ConventionProgrammeView",
)

cadastre_step = ConventionFormStep(
    pathname="conventions:cadastre",
    label="Cadastre",
    classname="ConventionCadastreView",
)

edd_step = ConventionFormStep(
    pathname="conventions:edd",
    label="EDD",
    classname="ConventionEDDView",
)

financement_step = ConventionFormStep(
    pathname="conventions:financement",
    label="Financement",
    classname="ConventionFinancementView",
)

logements_step = ConventionFormStep(
    pathname="conventions:logements",
    label="Logements",
    classname="ConventionLogementsView",
)

foyer_residence_logements_step = ConventionFormStep(
    pathname="conventions:foyer_residence_logements",
    label="Logements",
    classname="ConventionFoyerResidenceLogementsView",
)

annexes_step = ConventionFormStep(
    pathname="conventions:annexes",
    label="Annexes",
    classname="ConventionAnnexesView",
)

collectif_step = ConventionFormStep(
    pathname="conventions:collectif",
    label="Collectif",
    classname="ConventionCollectifView",
)

stationnements_step = ConventionFormStep(
    pathname="conventions:stationnements",
    label="Stationnements",
    classname="ConventionTypeStationnementView",
)

foyer_attribution_step = ConventionFormStep(
    pathname="conventions:attribution",
    label="Attribution",
    classname="ConventionFoyerAttributionView",
)

foyer_variante_step = ConventionFormStep(
    pathname="conventions:variantes",
    label="Variantes",
    classname="ConventionFoyerVariantesView",
)

comments_step = ConventionFormStep(
    pathname="conventions:comments",
    label="Commentaires",
    classname="ConventionCommentsView",
)

avenant_bailleur_step = ConventionFormStep(
    pathname="conventions:avenant_bailleur",
    label="Bailleur",
    classname="AvenantBailleurView",
)

avenant_logements_step = ConventionFormStep(
    pathname="conventions:avenant_logements",
    label="Logements",
    classname="AvenantLogementsView",
)

avenant_foyer_residence_logements_step = ConventionFormStep(
    pathname="conventions:avenant_foyer_residence_logements",
    label="Logements",
    classname="AvenantFoyerResidenceLogementsView",
)

avenant_annexes_step = ConventionFormStep(
    pathname="conventions:avenant_annexes",
    label="Annexes",
    classname="AvenantAnnexesView",
)

avenant_collectif_step = ConventionFormStep(
    pathname="conventions:avenant_collectif",
    label="Collectif",
    classname="AvenantCollectifView",
)

avenant_financement_step = ConventionFormStep(
    pathname="conventions:avenant_financement",
    label="Financement",
    classname="AvenantFinancementView",
)

avenant_comments_step = ConventionFormStep(
    pathname="conventions:avenant_comments",
    label="Commentaires",
    classname="AvenantCommentsView",
)


hlm_sem_type_steps = [
    bailleur_step,
    programme_step,
    cadastre_step,
    edd_step,
    financement_step,
    logements_step,
    annexes_step,
    stationnements_step,
    comments_step,
]

foyer_steps = [
    bailleur_step,
    programme_step,
    cadastre_step,
    edd_step,
    financement_step,
    foyer_residence_logements_step,
    collectif_step,
    foyer_attribution_step,
    foyer_variante_step,
    comments_step,
]


class ConventionFormSteps:
    steps: List[ConventionFormStep]
    convention: Convention
    total_step_number: int
    current_step_number: int
    current_step: ConventionFormStep
    next_step: ConventionFormStep
    previous_step: ConventionFormStep | None = None

    last_step_path: ConventionFormStep = ConventionFormStep(
        pathname="conventions:recapitulatif", label="Récapitulatif", classname=None
    )

    def __init__(self, *, convention, active_classname=None) -> None:
        # pylint: disable=R0912
        self.convention = convention
        if convention.is_avenant():
            if active_classname is None:
                if convention.programme.is_foyer():
                    self.steps = [
                        avenant_bailleur_step,
                        avenant_financement_step,
                        avenant_foyer_residence_logements_step,
                        avenant_collectif_step,
                        avenant_comments_step,
                    ]
                else:
                    self.steps = [
                        avenant_bailleur_step,
                        avenant_financement_step,
                        avenant_logements_step,
                        avenant_annexes_step,
                        avenant_comments_step,
                    ]
            else:
                if active_classname == "AvenantBailleurView":
                    self.steps = [avenant_bailleur_step]
                if active_classname in [
                    "AvenantLogementsView",
                    "AvenantAnnexesView",
                ]:
                    self.steps = [avenant_logements_step, avenant_annexes_step]
                if active_classname in [
                    "AvenantFoyerResidenceLogementsView",
                    "AvenantCollectifView",
                ]:
                    self.steps = [
                        avenant_foyer_residence_logements_step,
                        avenant_collectif_step,
                    ]
                if active_classname == "AvenantFinancementView":
                    self.steps = [avenant_financement_step]
                if active_classname == "AvenantCommentsView":
                    self.steps = [avenant_comments_step]
        elif convention.programme.is_foyer():
            self.steps = foyer_steps
        else:
            self.steps = hlm_sem_type_steps

        self.total_step_number = len(self.steps)

        if active_classname is not None:
            step_index = [
                i
                for i, elem in enumerate(self.steps)
                if elem.classname == active_classname
            ][0]
            self.current_step_number = step_index + 1
            self.current_step = self.steps[step_index]
            self.next_step = (
                self.steps[step_index + 1]
                if self.current_step_number < self.total_step_number
                else self.last_step_path
            )
            if step_index > 0:
                self.previous_step = self.steps[step_index - 1]

    def get_form_step(self):
        form_step = {
            "number": self.current_step_number,
            "total": self.total_step_number,
            "title": self.current_step.label,
            "next": self.next_step.label,
            "next_target": self.next_step.pathname,
        }
        if self.previous_step is not None:
            form_step.update(
                {
                    "previous": self.previous_step.label,
                    "previous_target": self.previous_step.pathname,
                }
            )
        return form_step

    def next_path_redirect(self):
        return self.next_step.pathname

    def current_step_path(self):
        return self.current_step.pathname


class ConventionView(ABC, LoginRequiredMixin, View):
    convention: Convention
    steps: ConventionFormSteps
    target_template: str
    service_class: ConventionService

    def _get_convention(self, convention_uuid):
        # pylint: disable=R0201
        return Convention.objects.get(uuid=convention_uuid)

    @property
    def next_path_redirect(self):
        return self.steps.next_path_redirect()

    def current_path_redirect(self):
        return self.steps.current_step_path()

    # pylint: disable=W0221
    def setup(self, request, convention_uuid, *args, **kwargs):
        self.convention = self._get_convention(convention_uuid)
        self.steps = ConventionFormSteps(
            convention=self.convention, active_classname=self.__class__.__name__
        )
        return super().setup(request, convention_uuid, *args, **kwargs)

    # pylint: disable=W0613
    @has_campaign_permission("convention.view_convention")
    def get(self, request, convention_uuid):
        service = self.service_class(convention=self.convention, request=request)
        service.get()
        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                "form_step": self.steps.get_form_step(),
                "editable_after_upload": (
                    editable_convention(request, self.convention)
                    or service.editable_after_upload
                ),
            },
        )

    # pylint: disable=W0613
    @has_campaign_permission("convention.change_convention")
    def post(self, request, convention_uuid):
        service = self.service_class(convention=self.convention, request=request)
        service.save()
        if service.return_status == ReturnStatus.SUCCESS:
            if service.redirect_recap:
                return HttpResponseRedirect(
                    reverse("conventions:recapitulatif", args=[self.convention.uuid])
                )
            return HttpResponseRedirect(
                reverse(self.next_path_redirect, args=[self.convention.uuid])
            )
        if service.return_status == ReturnStatus.REFRESH:
            return HttpResponseRedirect(
                reverse(self.current_path_redirect, args=[self.convention.uuid])
            )
        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                "form_step": self.steps.get_form_step(),
                **(
                    {"import_warnings": service.import_warnings}
                    if service.import_warnings
                    else {}
                ),
                "editable_after_upload": editable_convention(request, self.convention)
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
    current_path_redirect: str = "conventions:bailleur"
    service_class = ConventionBailleurService


class AvenantBailleurView(ConventionBailleurView):
    current_path_redirect: str = "conventions:avenant_bailleur"


class ConventionProgrammeView(ConventionView):
    target_template: str = "conventions/programme.html"
    service_class = ConventionProgrammeService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("lot")
            .get(uuid=convention_uuid)
        )


class ConventionCadastreView(ConventionView):
    target_template: str = "conventions/cadastre.html"
    service_class = ConventionCadastreService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("programme__referencecadastrales")
            .get(uuid=convention_uuid)
        )


class ConventionEDDView(ConventionView):
    target_template: str = "conventions/edd.html"
    service_class = ConventionEDDService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("lot")
            .prefetch_related("programme__logementedds")
            .get(uuid=convention_uuid)
        )


class ConventionFinancementView(ConventionView):
    target_template: str = "conventions/financement.html"
    service_class = ConventionFinancementService

    def _get_convention(self, convention_uuid):
        return Convention.objects.prefetch_related("prets").get(uuid=convention_uuid)


class AvenantFinancementView(ConventionFinancementView):
    pass


class ConventionLogementsView(ConventionView):
    target_template: str = "conventions/logements.html"
    service_class = ConventionLogementsService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements")
            .get(uuid=convention_uuid)
        )


class AvenantLogementsView(ConventionLogementsView):
    pass


class ConventionFoyerResidenceLogementsView(ConventionView):
    target_template: str = "conventions/foyer_residence_logements.html"
    service_class = ConventionFoyerResidenceLogementsService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements")
            .get(uuid=convention_uuid)
        )


class AvenantFoyerResidenceLogementsView(ConventionFoyerResidenceLogementsView):
    pass


class ConventionAnnexesView(ConventionView):
    target_template: str = "conventions/annexes.html"
    service_class = ConventionAnnexesService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements__annexes")
            .get(uuid=convention_uuid)
        )


class AvenantAnnexesView(ConventionAnnexesView):
    pass


class ConventionCollectifView(ConventionView):
    target_template: str = "conventions/collectif.html"
    service_class = ConventionCollectifService

    def _get_convention(self, convention_uuid):
        return (
            Convention.objects.prefetch_related("lot")
            .prefetch_related("lot__logements__annexes")
            .get(uuid=convention_uuid)
        )


class AvenantCollectifView(ConventionCollectifView):
    pass


class ConventionFoyerAttributionView(ConventionView):
    target_template: str = "conventions/attribution.html"
    service_class = ConventionFoyerAttributionService


class ConventionFoyerVariantesView(ConventionView):
    target_template: str = "conventions/variantes.html"
    service_class = ConventionFoyerVariantesService


class ConventionTypeStationnementView(ConventionView):
    target_template: str = "conventions/stationnements.html"
    service_class = ConventionTypeStationnementService


class ConventionCommentsView(ConventionView):
    target_template: str = "conventions/comments.html"
    service_class = ConventionCommentsService


class AvenantCommentsView(ConventionCommentsView):
    pass
