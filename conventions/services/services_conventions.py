import datetime
from typing import Any, List
from abc import ABC

from django.forms import Form

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.db.models.functions import Substr
from django.http.request import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from comments.models import Comment, CommentStatut
from conventions.forms import (
    ConventionCommentForm,
    ConventionFinancementForm,
    ConventionNumberForm,
    ConventionResiliationForm,
    ConventionType1and2Form,
    AvenantForm,
    NotificationForm,
    PretFormSet,
    UploadForm,
)
from conventions.models import (
    AvenantType,
    Convention,
    ConventionHistory,
    ConventionStatut,
    Pret,
)
from conventions.services import convention_generator, upload_objects, utils
from conventions.tasks import generate_and_send
from core.services import EmailService
from programmes.models import Annexe, Financement
from siap.siap_client.client import SIAPClient
from upload.services import UploadService


class ConventionService(ABC):
    convention: Convention
    request: HttpRequest
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    import_warnings: None | List = None
    redirect_recap: bool = False
    editable_after_upload: bool = False
    form: Form = None
    formset = None
    upform = None

    def __init__(
        self,
        convention: Convention,
        request: HttpRequest,
    ):
        self.convention = convention
        self.request = request

    def get(self):
        pass

    def save(self):
        pass


@require_GET
def conventions_index(request):

    convention_list_service = ConventionListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "lot__programme__date_achevement_compile"),
        page=request.GET.get("page", 1),
        statut_filter=request.GET.get("cstatut", ""),
        financement_filter=request.GET.get("financement", ""),
        departement_input=request.GET.get("departement_input", ""),
        my_convention_list=request.user.conventions()
        .prefetch_related("lot")
        .prefetch_related("lot__programme")
        .prefetch_related("lot__programme__administration"),
    )
    convention_list_service.paginate()

    return {
        "conventions": convention_list_service,
        "statuts": ConventionStatut,
        "financements": Financement,
    }


def _save_convention_type(request, convention):
    convention_type1_and_2_form = ConventionType1and2Form(request.POST)
    if convention_type1_and_2_form.is_valid():
        convention.type1and2 = (
            convention_type1_and_2_form.cleaned_data["type1and2"]
            if convention_type1_and_2_form.cleaned_data["type1and2"]
            else None
        )
        if "type2_lgts_concernes_option1" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option1 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option1"]
            )
        if "type2_lgts_concernes_option2" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option2 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option2"]
            )
        if "type2_lgts_concernes_option3" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option3 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option3"]
            )
        if "type2_lgts_concernes_option4" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option4 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option4"]
            )
        if "type2_lgts_concernes_option5" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option5 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option5"]
            )
        if "type2_lgts_concernes_option6" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option6 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option6"]
            )
        if "type2_lgts_concernes_option7" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option7 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option7"]
            )
        if "type2_lgts_concernes_option8" in convention_type1_and_2_form.cleaned_data:
            convention.type2_lgts_concernes_option8 = (
                convention_type1_and_2_form.cleaned_data["type2_lgts_concernes_option8"]
            )
        convention.save()
    return convention_type1_and_2_form


def convention_summary(request, convention):
    request.user.check_perm("convention.view_convention", convention)
    convention_number_form = ConventionNumberForm(
        initial={"convention_numero": convention.get_default_convention_number()}
    )

    opened_comments = Comment.objects.filter(
        convention=convention,
        statut=CommentStatut.OUVERT,
    )
    opened_comments = opened_comments.order_by("cree_le")
    if request.method == "POST":
        convention_type1_and_2_form = _save_convention_type(request, convention)
    else:
        convention_type1_and_2_form = ConventionType1and2Form(
            initial={
                "uuid": convention.uuid,
                "type1and2": convention.type1and2,
                "type2_lgts_concernes_option1": convention.type2_lgts_concernes_option1,
                "type2_lgts_concernes_option2": convention.type2_lgts_concernes_option2,
                "type2_lgts_concernes_option3": convention.type2_lgts_concernes_option3,
                "type2_lgts_concernes_option4": convention.type2_lgts_concernes_option4,
                "type2_lgts_concernes_option5": convention.type2_lgts_concernes_option5,
                "type2_lgts_concernes_option6": convention.type2_lgts_concernes_option6,
                "type2_lgts_concernes_option7": convention.type2_lgts_concernes_option7,
                "type2_lgts_concernes_option8": convention.type2_lgts_concernes_option8,
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "opened_comments": opened_comments,
        "bailleur": convention.lot.programme.bailleur,
        "lot": convention.lot,
        "programme": convention.lot.programme,
        "logement_edds": convention.lot.programme.logementedds.all(),
        "logements": convention.lot.logements.all(),
        "stationnements": convention.lot.type_stationnements.all(),
        "reference_cadastrales": convention.lot.programme.referencecadastrales.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
        "notificationForm": NotificationForm(),
        "conventionNumberForm": convention_number_form,
        "ConventionType1and2Form": convention_type1_and_2_form,
    }


@require_POST
def convention_submit(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    submitted = utils.ReturnStatus.WARNING
    request.user.check_perm("convention.change_convention", convention)
    # Set back the onvention to the instruction
    if request.POST.get("BackToInstruction", False):
        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION,
            statut_convention_precedent=convention.statut,
            user=request.user,
        ).save()
        convention.statut = ConventionStatut.INSTRUCTION
        convention.save()
        submitted = utils.ReturnStatus.ERROR
    # Submit the convention to the instruction
    if request.POST.get("SubmitConvention", False):

        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION,
            statut_convention_precedent=convention.statut,
            user=request.user,
        ).save()

        if convention.premiere_soumission_le is None:
            convention.premiere_soumission_le = timezone.now()
        convention.soumis_le = timezone.now()
        convention.statut = ConventionStatut.INSTRUCTION
        convention.save()

        instructeur_emails = []
        if request.user.is_cerbere_user():
            client = SIAPClient.get_instance()
            operation = client.get_operation(
                user_login=request.user.cerbere_login,
                habilitation_id=request.session["habilitation_id"],
                operation_identifier=convention.lot.programme.numero_galion,
            )
            for utilisateur in operation["gestionnaire"]["utilisateurs"]:
                instructeur_emails.append(utilisateur["email"])
        else:
            instructeur_emails = convention.get_email_instructeur_users(
                include_partial=True
            )

        send_email_instruction(
            request.build_absolute_uri(
                reverse("conventions:recapitulatif", args=[convention.uuid])
            ),
            convention,
            instructeur_emails,
        )
        submitted = utils.ReturnStatus.SUCCESS
    return {
        "success": submitted,
        "convention": convention,
    }


@require_GET
def convention_delete(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.change_convention", convention)
    convention.delete()


def send_email_instruction(convention_url, convention, instructeur_emails):
    """
    Send email "convention à instruire" when bailleur submit the convention
    Send an email to the bailleur who click and bailleur TOUS
    Send an email to all instructeur (except the ones who select AUCUN as email preference)
    """
    email_sent = []

    if convention.is_avenant():
        template_label = "avenants/toB_instruction"
    else:
        template_label = "conventions/toB_instruction"

    # envoi au bailleur
    text_content = render_to_string(
        f"emails/{template_label}.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )
    html_content = render_to_string(
        f"emails/{template_label}.html",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )

    email_service = EmailService(
        subject=f"Convention à instruire ({convention})",
        to_emails=convention.get_email_bailleur_users(),
        text_content=text_content,
        html_content=html_content,
    )
    email_service.send()
    email_sent.append(email_service.msg)

    if convention.is_avenant():
        template_label = "avenants/BtoI_convention_to_instruction"
    else:
        template_label = "conventions/BtoI_convention_to_instruction"

    # envoie à l'instructeur
    text_content = render_to_string(
        f"emails/{template_label}.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )
    html_content = render_to_string(
        f"emails/{template_label}.html",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )

    email_service = EmailService(
        subject=f"Convention à instruire ({convention})",
        to_emails=instructeur_emails,
        text_content=text_content,
        html_content=html_content,
    )
    email_service.send()
    email_sent.append(email_service.msg)

    return email_sent


@require_POST
def convention_feedback(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    notification_form = NotificationForm(request.POST)
    if notification_form.is_valid():
        cc = [request.user.email] if notification_form.cleaned_data["send_copy"] else []
        send_email_correction(
            request.build_absolute_uri(
                reverse("conventions:recapitulatif", args=[convention.uuid]),
            ),
            convention,
            cc,
            notification_form.cleaned_data["from_instructeur"],
            notification_form.cleaned_data["comment"],
            all_bailleur_users=(notification_form.cleaned_data["all_bailleur_users"]),
        )
        target_status = ConventionStatut.INSTRUCTION
        if notification_form.cleaned_data["from_instructeur"]:
            target_status = ConventionStatut.CORRECTION
        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=target_status,
            statut_convention_precedent=convention.statut,
            user=request.user,
            commentaire=notification_form.cleaned_data["comment"],
        ).save()
        convention.statut = target_status
        convention.save()

        return utils.base_response_redirect_recap_success(convention)
    return {
        **utils.base_convention_response_error(request, convention),
        "notificationForm": notification_form,
    }


def send_email_correction(
    convention_url,
    convention,
    cc,
    from_instructeur,
    comment=None,
    all_bailleur_users=False,
):
    """
    send email to notify correction is needed of correction is done:
    * corrections are needed => send to bailleur who interact + PARTIEL
        and bailleur who select TOUS as email preferences
    * corrections are done -> send email to instructeur who interact + PARTIEL and instructeur TOUS
    """
    if from_instructeur:
        # Get bailleurs list following email preferences and interaction with the convention
        to = convention.get_email_bailleur_users(all_bailleur_users=all_bailleur_users)
        subject = f"Convention à modifier ({convention})"
        if convention.is_avenant():
            template_label = "avenants/ItoB_correction_needed"
        else:
            template_label = "conventions/ItoB_correction_needed"

    else:
        # Get instructeurs list following email preferences and interaction with the convention
        to = convention.get_email_instructeur_users()
        subject = f"Convention modifiée ({convention})"
        if convention.is_avenant():
            template_label = "avenants/BtoI_correction_done"
        else:
            template_label = "conventions/BtoI_correction_done"

    text_content = render_to_string(
        f"emails/{template_label}.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
            "commentaire": comment,
        },
    )
    html_content = render_to_string(
        f"emails/{template_label}.html",
        {
            "convention_url": convention_url,
            "convention": convention,
            "commentaire": comment,
        },
    )

    email_service = EmailService(
        subject=subject,
        to_emails=to,
        cc_emails=cc,
        text_content=text_content,
        html_content=html_content,
    )
    email_service.send()

    return email_service.msg


@require_POST
def convention_validate(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.change_convention", convention)

    convention_number_form = ConventionNumberForm(request.POST)
    convention_number_form.convention = convention
    if convention_number_form.is_valid():
        convention.numero = convention_number_form.cleaned_data["convention_numero"]

        convention.save()

    if convention_number_form.is_valid() or request.POST.get("Force"):

        # Generate the doc should be placed after the status update
        # because the watermark report the status of the convention
        previous_status = convention.statut
        convention.statut = ConventionStatut.A_SIGNER

        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=ConventionStatut.A_SIGNER,
            statut_convention_precedent=previous_status,
            user=request.user,
        ).save()

        generate_and_send.send(
            {
                "convention_uuid": str(convention.uuid),
                "convention_recapitulatif_uri": request.build_absolute_uri(
                    reverse("conventions:recapitulatif", args=[convention.uuid])
                ),
                "convention_email_validator": request.user.email,
            }
        )
        if not convention.valide_le:
            convention.valide_le = timezone.now()
        convention.save()

        return {
            "success": utils.ReturnStatus.SUCCESS,
            "convention": convention,
        }

    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__programme__bailleur")
        .prefetch_related("lot__programme__referencecadastrales")
        .prefetch_related("lot__programme__logementedds")
        .prefetch_related("lot__type_stationnements")
        .prefetch_related("lot__logements")
        .get(uuid=convention_uuid)
    )
    return {
        **utils.base_convention_response_error(request, convention),
        "bailleur": convention.lot.programme.bailleur,
        "lot": convention.lot,
        "programme": convention.lot.programme,
        "logement_edds": convention.lot.programme.logementedds.all(),
        "logements": convention.lot.logements.all(),
        "stationnements": convention.lot.type_stationnements.all(),
        "reference_cadastrales": convention.lot.programme.referencecadastrales.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
        "notificationForm": NotificationForm(),
        "conventionNumberForm": convention_number_form,
    }


@require_POST
def generate_convention_service(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__type_stationnements")
        .prefetch_related("lot__logements")
        .prefetch_related("prets")
        .prefetch_related("lot__programme")
        .prefetch_related("lot__programme__bailleur")
        .prefetch_related("lot__programme__administration")
        .prefetch_related("lot__programme__logementedds")
        .prefetch_related("lot__programme__referencecadastrales")
        .get(uuid=convention_uuid)
    )
    file_stream = convention_generator.generate_convention_doc(convention)

    return file_stream, f"{convention}"


class ConventionListService:
    # pylint: disable=R0902,R0903,R0913
    search_input: str
    order_by: str
    page: str
    statut_filter: str
    financement_filter: str
    departement_input: str
    my_convention_list: Any  # list[Convention]
    paginated_conventions: Any  # list[Convention]
    total_conventions: int

    def __init__(
        self,
        my_convention_list: Any,
        search_input: str = "",
        statut_filter: str = "",
        financement_filter: str = "",
        departement_input: str = "",
        order_by: str = "",
        page: str = 1,
    ):
        self.search_input = search_input
        self.statut_filter = statut_filter
        self.financement_filter = financement_filter
        self.departement_input = departement_input
        self.order_by = order_by
        self.page = page
        self.my_convention_list = my_convention_list

    def paginate(self) -> None:
        total_user = self.my_convention_list.count()
        if self.search_input:
            self.my_convention_list = self.my_convention_list.filter(
                Q(lot__programme__ville__icontains=self.search_input)
                | Q(lot__programme__nom__icontains=self.search_input)
                | Q(lot__programme__numero_galion__icontains=self.search_input)
            )
        if self.statut_filter:
            self.my_convention_list = self.my_convention_list.filter(
                statut=self.statut_filter
            )
        if self.financement_filter:
            self.my_convention_list = self.my_convention_list.filter(
                lot__financement=self.financement_filter
            )
        if self.departement_input:
            self.my_convention_list = self.my_convention_list.annotate(
                departement=Substr("lot__programme__code_postal", 1, 2)
            ).filter(departement=self.departement_input)

        if self.order_by:
            self.my_convention_list = self.my_convention_list.order_by(self.order_by)

        paginator = Paginator(
            self.my_convention_list, settings.APILOS_PAGINATION_PER_PAGE
        )
        try:
            conventions = paginator.page(self.page)
        except PageNotAnInteger:
            conventions = paginator.page(1)
        except EmptyPage:
            conventions = paginator.page(paginator.num_pages)

        self.paginated_conventions = conventions
        self.total_conventions = total_user


def convention_preview(convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    return {
        "convention": convention,
    }


def convention_sent(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    result_status = None
    if request.method == "POST":
        upform = UploadForm(request.POST, request.FILES)
        if upform.is_valid():
            file = request.FILES["file"]
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"{now}_convention_{convention_uuid}_signed.pdf"
            upload_service = UploadService(
                convention_dirpath=f"conventions/{convention_uuid}/convention_docs",
                filename=filename,
            )
            upload_service.upload_file(file)

            convention.statut = ConventionStatut.SIGNEE
            convention.nom_fichier_signe = filename
            convention.televersement_convention_signee_le = timezone.now()
            convention.save()
            result_status = utils.ReturnStatus.SUCCESS
    else:
        upform = UploadForm()

    return {
        "success": result_status,
        "convention": convention,
        "upform": upform,
    }


def convention_post_action(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    result_status = None
    if request.method == "POST":
        resiliation_form = ConventionResiliationForm(request.POST)
        if resiliation_form.is_valid():
            convention.statut = ConventionStatut.RESILIEE
            convention.date_resiliation = resiliation_form.cleaned_data[
                "date_resiliation"
            ]
            convention.save()
            # SUCCESS
            result_status = utils.ReturnStatus.SUCCESS

    else:
        resiliation_form = ConventionResiliationForm()

    upform = UploadForm()
    avenant_list_service = ConventionListService(
        my_convention_list=convention.avenants.all()
        .prefetch_related("lot__programme")
        .prefetch_related("lot"),
        order_by="cree_le",
    )
    total_avenants = convention.avenants.all().count()
    avenant_list_service.paginate()

    return {
        "success": result_status,
        "upform": upform,
        "convention": convention,
        "avenants": avenant_list_service,
        "total_avenants": total_avenants,
        "resiliation_form": resiliation_form,
    }


def _get_last_avenant(convention):
    avenants_status = {avenant.statut for avenant in convention.avenants.all()}
    if {
        ConventionStatut.PROJET,
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
    } & avenants_status:
        raise Exception("Ongoing avenant already exists")
    ordered_avenants = convention.avenants.order_by("-cree_le")
    return ordered_avenants[0] if ordered_avenants else convention


def create_avenant(request, convention_uuid):
    parent_convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__programme")
        .prefetch_related("avenants")
        .get(uuid=convention_uuid)
    )
    if request.method == "POST":
        avenant_form = AvenantForm(request.POST)
        if avenant_form.is_valid():
            if avenant_form.cleaned_data["uuid"]:
                avenant = Convention.objects.get(uuid=avenant_form.cleaned_data["uuid"])
            else:
                convention_to_clone = _get_last_avenant(parent_convention)
                avenant = convention_to_clone.clone(
                    request.user, convention_origin=parent_convention
                )
            avenant_type = AvenantType.objects.get(
                nom=avenant_form.cleaned_data["avenant_type"]
            )
            avenant.avenant_types.add(avenant_type)
            avenant.save()
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": avenant,
                "parent_convention": parent_convention,
                "avenant_type": avenant_type,
            }
    else:
        avenant_form = AvenantForm()

    return {
        "success": utils.ReturnStatus.ERROR,
        "editable": request.user.has_perm("convention.add_convention"),
        "bailleurs": request.user.bailleurs(),
        "form": avenant_form,
        "parent_convention": parent_convention,
    }


class ConventionFinancementService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ConventionFinancementForm
    formset = None
    upform: UploadForm = UploadForm()
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False
    editable_after_upload: bool = False

    def get(self):
        initial = []
        prets = self.convention.prets.all()
        for pret in prets:
            initial.append(
                {
                    "uuid": pret.uuid,
                    "numero": pret.numero,
                    "date_octroi": utils.format_date_for_form(pret.date_octroi),
                    "duree": pret.duree,
                    "montant": pret.montant,
                    "preteur": pret.preteur,
                    "autre": pret.autre,
                }
            )
        self.formset = PretFormSet(initial=initial)
        self.form = ConventionFinancementForm(
            initial={
                "uuid": self.convention.uuid,
                "annee_fin_conventionnement": str(
                    self.convention.date_fin_conventionnement.year
                )
                if self.convention.date_fin_conventionnement is not None
                else None,
                "fond_propre": self.convention.fond_propre,
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        # When the user cliked on "Téléverser" button
        if self.request.POST.get("Upload", False):
            self.form = ConventionFinancementForm(self.request.POST)
            self._upload_prets()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._convention_financement_atomic_update()

    def _upload_prets(self):
        self.formset = PretFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():

            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                Pret,
                self.convention,
                "financement.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:

                prets_by_numero = {}
                for pret in self.convention.prets.all():
                    prets_by_numero[pret.numero] = pret.uuid
                for obj in result["objects"]:
                    if "numero" in obj and obj["numero"] in prets_by_numero:
                        obj["uuid"] = prets_by_numero[obj["numero"]]

                self.formset = PretFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _convention_financement_atomic_update(self):
        self.form = ConventionFinancementForm(
            {
                "uuid": self.convention.uuid,
                "fond_propre": self.request.POST.get(
                    "fond_propre", self.convention.fond_propre
                ),
                "annee_fin_conventionnement": self.request.POST.get(
                    "annee_fin_conventionnement",
                    self.convention.date_fin_conventionnement.year
                    if self.convention.date_fin_conventionnement is not None
                    else None,
                ),
            }
        )

        self.formset = PretFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_pret in enumerate(self.formset):
            if form_pret["uuid"].value():
                pret = Pret.objects.get(uuid=form_pret["uuid"].value())
                initformset = {
                    **initformset,
                    f"form-{idx}-uuid": pret.uuid,
                    f"form-{idx}-numero": utils.get_form_value(
                        form_pret, pret, "numero"
                    ),
                    f"form-{idx}-date_octroi": utils.get_form_date_value(
                        form_pret, pret, "date_octroi"
                    ),
                    f"form-{idx}-duree": utils.get_form_value(form_pret, pret, "duree"),
                    f"form-{idx}-montant": utils.get_form_value(
                        form_pret, pret, "montant"
                    ),
                    f"form-{idx}-preteur": utils.get_form_value(
                        form_pret, pret, "preteur"
                    ),
                    f"form-{idx}-autre": utils.get_form_value(form_pret, pret, "autre"),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-numero": form_pret["numero"].value(),
                    f"form-{idx}-date_octroi": form_pret["date_octroi"].value(),
                    f"form-{idx}-duree": form_pret["duree"].value(),
                    f"form-{idx}-montant": form_pret["montant"].value(),
                    f"form-{idx}-preteur": form_pret["preteur"].value(),
                    f"form-{idx}-autre": form_pret["autre"].value(),
                }
        self.formset = PretFormSet(initformset)
        self.formset.convention = self.convention

        if self.formset.is_valid():
            self.form.prets = self.formset
            self.form.convention = self.convention
            if self.form.is_valid():
                self._save_convention_financement()
                self._save_convention_financement_prets()
                self.return_status = utils.ReturnStatus.SUCCESS
                self.redirect_recap = self.request.POST.get("redirect_to_recap", False)

    def _save_convention_financement(self):
        self.convention.date_fin_conventionnement = datetime.date(
            self.form.cleaned_data["annee_fin_conventionnement"], 6, 30
        )
        self.convention.fond_propre = self.form.cleaned_data["fond_propre"]
        self.convention.save()

    def _save_convention_financement_prets(self):
        obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        obj_uuids = list(filter(None, obj_uuids1))
        self.convention.prets.exclude(uuid__in=obj_uuids).delete()
        for form_pret in self.formset:
            if form_pret.cleaned_data["uuid"]:
                pret = Pret.objects.get(uuid=form_pret.cleaned_data["uuid"])
                pret.numero = form_pret.cleaned_data["numero"]
                pret.date_octroi = form_pret.cleaned_data["date_octroi"]
                pret.duree = form_pret.cleaned_data["duree"]
                pret.montant = form_pret.cleaned_data["montant"]
                pret.preteur = form_pret.cleaned_data["preteur"]
                pret.autre = form_pret.cleaned_data["autre"]

            else:
                pret = Pret.objects.create(
                    convention=self.convention,
                    numero=form_pret.cleaned_data["numero"],
                    date_octroi=form_pret.cleaned_data["date_octroi"],
                    duree=form_pret.cleaned_data["duree"],
                    montant=form_pret.cleaned_data["montant"],
                    preteur=form_pret.cleaned_data["preteur"],
                    autre=form_pret.cleaned_data["autre"],
                )
            pret.save()


class ConventionCommentsService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ConventionCommentForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionCommentForm(
            initial={
                "uuid": self.convention.uuid,
                "comments": self.convention.comments,
                **utils.get_text_and_files_from_field(
                    "comments", self.convention.comments
                ),
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.form = ConventionCommentForm(self.request.POST)
        if self.form.is_valid():
            self.convention.comments = utils.set_files_and_text_field(
                self.form.cleaned_data["comments_files"],
                self.form.cleaned_data["comments"],
            )
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS
