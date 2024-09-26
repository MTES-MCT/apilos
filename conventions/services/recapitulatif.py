import datetime
from typing import List

from django.db.models import Q
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

from comments.models import Comment, CommentStatut
from conventions.forms.avenant import CompleteforavenantForm
from conventions.forms.convention_form_dates import ConventionDateSignatureForm
from conventions.forms.convention_number import ConventionNumberForm
from conventions.forms.notification import NotificationForm
from conventions.forms.programme_number import ProgrammeNumberForm
from conventions.forms.type1and2 import ConventionType1and2Form
from conventions.forms.upload import UploadForm
from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from conventions.models.convention_history import ConventionHistory
from conventions.services import utils
from conventions.services.conventions import ConventionService
from conventions.services.file import ConventionFileService
from conventions.tasks import task_generate_and_send
from core.request import AuthenticatedHttpRequest
from core.services import EmailService, EmailTemplateID
from core.stepper import Stepper
from programmes.models import Annexe, Programme
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from users.models import GroupProfile, User
from users.type_models import EmailPreferences


class ConventionRecapitulatifService(ConventionService):
    def get(self):
        pass

    def save(self):
        pass

    def cancel_convention(self):
        self.convention.cancel(self.request)
        return {}

    def reactive_convention(self):
        if self.convention.statut != ConventionStatut.ANNULEE.label:
            return {}
        previous_status = self.convention.statut
        self.convention.statut = ConventionStatut.PROJET.label
        self.convention.save()
        ConventionHistory.objects.create(
            convention=self.convention,
            statut_convention=ConventionStatut.PROJET.label,
            statut_convention_precedent=previous_status,
            user=self.request.user,
        ).save()
        return {}

    def update_programme_number(self):
        programme_number_form = ProgrammeNumberForm(self.request.POST)
        if programme_number_form.is_valid():
            self.convention.programme.numero_operation = (
                programme_number_form.cleaned_data["numero_operation"]
            )
            programme_id = (
                self.convention.parent.programme_id
                if self.convention.parent
                else self.convention.programme_id
            )
            for programme in Programme.objects.filter(
                Q(id=programme_id) | Q(parent_id=programme_id)
            ):
                programme.numero_operation = programme_number_form.cleaned_data[
                    "numero_operation"
                ]
                programme.save()
        return self.get_convention_recapitulatif(
            programme_number_form=programme_number_form
        )

    def update_convention_number(self):
        convention_number_form = ConventionNumberForm(self.request.POST)
        convention_number_form.convention = self.convention
        if convention_number_form.is_valid():
            self.convention.numero = convention_number_form.cleaned_data[
                "convention_numero"
            ]
            self.convention.save()
        return self.get_convention_recapitulatif(
            convention_number_form=convention_number_form
        )

    def get_convention_recapitulatif(
        self,
        convention_type1_and_2_form=None,
        programme_number_form=None,
        convention_number_form=None,
    ):
        if convention_number_form is None:
            convention_number_form = ConventionNumberForm(
                initial={
                    "convention_numero": self.convention.get_default_convention_number()
                }
            )

        if programme_number_form is None:
            programme_number_form = ProgrammeNumberForm(
                initial={"numero_operation": self.convention.programme.numero_operation}
            )

        complete_for_avenant_form = None
        if self.convention.is_incompleted_avenant_parent():
            complete_for_avenant_form = CompleteforavenantForm(
                initial={
                    "ville": self.convention.parent.programme.ville,
                    "nb_logements": self.convention.parent.lot.nb_logements,
                }
            )

        opened_comments = Comment.objects.filter(
            convention=self.convention,
            statut=CommentStatut.OUVERT,
        ).order_by("cree_le")
        if convention_type1_and_2_form is None:
            convention_type1_and_2_form = ConventionType1and2Form(
                initial={
                    "uuid": self.convention.uuid,
                    "type1and2": self.convention.type1and2,
                    "type2_lgts_concernes_option1": self.convention.type2_lgts_concernes_option1,
                    "type2_lgts_concernes_option2": self.convention.type2_lgts_concernes_option2,
                    "type2_lgts_concernes_option3": self.convention.type2_lgts_concernes_option3,
                    "type2_lgts_concernes_option4": self.convention.type2_lgts_concernes_option4,
                    "type2_lgts_concernes_option5": self.convention.type2_lgts_concernes_option5,
                    "type2_lgts_concernes_option6": self.convention.type2_lgts_concernes_option6,
                    "type2_lgts_concernes_option7": self.convention.type2_lgts_concernes_option7,
                    "type2_lgts_concernes_option8": self.convention.type2_lgts_concernes_option8,
                }
            )
        return {
            "opened_comments": opened_comments,
            "annexes": Annexe.objects.filter(
                logement__lot_id=self.convention.lot_id
            ).all(),
            "notificationForm": NotificationForm(),
            "conventionNumberForm": convention_number_form,
            "complete_for_avenant_form": complete_for_avenant_form,
            "ConventionType1and2Form": convention_type1_and_2_form,
            "programmeNumberForm": programme_number_form,
            "repartition_surfaces": self.convention.lot.repartition_surfaces(),
        }

    def save_convention_type_1_and_2(self):
        convention_type1_and_2_form = ConventionType1and2Form(self.request.POST)
        if convention_type1_and_2_form.is_valid():
            self.convention.type1and2 = (
                convention_type1_and_2_form.cleaned_data["type1and2"]
                if convention_type1_and_2_form.cleaned_data["type1and2"]
                else None
            )
            if (
                "type2_lgts_concernes_option1"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option1 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option1"
                    ]
                )
            if (
                "type2_lgts_concernes_option2"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option2 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option2"
                    ]
                )
            if (
                "type2_lgts_concernes_option3"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option3 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option3"
                    ]
                )
            if (
                "type2_lgts_concernes_option4"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option4 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option4"
                    ]
                )
            if (
                "type2_lgts_concernes_option5"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option5 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option5"
                    ]
                )
            if (
                "type2_lgts_concernes_option6"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option6 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option6"
                    ]
                )
            if (
                "type2_lgts_concernes_option7"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option7 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option7"
                    ]
                )
            if (
                "type2_lgts_concernes_option8"
                in convention_type1_and_2_form.cleaned_data
            ):
                self.convention.type2_lgts_concernes_option8 = (
                    convention_type1_and_2_form.cleaned_data[
                        "type2_lgts_concernes_option8"
                    ]
                )
            self.convention.save()
        return self.get_convention_recapitulatif(
            convention_type1_and_2_form=convention_type1_and_2_form
        )


def convention_submit(request: HttpRequest, convention: Convention):
    submitted = utils.ReturnStatus.REFRESH
    # Set back the onvention to the instruction
    if request.POST.get("BackToInstruction", False):
        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION.label,
            statut_convention_precedent=convention.statut,
            user=request.user,
        ).save()
        convention.statut = ConventionStatut.INSTRUCTION.label
        convention.save()
        submitted = utils.ReturnStatus.ERROR
    # Submit the convention to the instruction
    if request.POST.get("SubmitConvention", False):
        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION.label,
            statut_convention_precedent=convention.statut,
            user=request.user,
        ).save()

        if convention.premiere_soumission_le is None:
            convention.premiere_soumission_le = timezone.now()
        convention.soumis_le = timezone.now()
        convention.statut = ConventionStatut.INSTRUCTION.label
        convention.save()

        instructeur_emails, submitted = collect_instructeur_emails(
            request, convention, submitted
        )
        send_email_instruction(
            request.build_absolute_uri(
                reverse("conventions:recapitulatif", args=[convention.uuid])
            ),
            convention,
            request.user,
            instructeur_emails,
        )
        if submitted != utils.ReturnStatus.WARNING:
            submitted = utils.ReturnStatus.SUCCESS
    return {
        "success": submitted,
        "convention": convention,
    }


def collect_instructeur_emails(
    request: HttpRequest,
    convention: Convention,
    submitted: utils.ReturnStatus = utils.ReturnStatus.REFRESH,
) -> List[str]:
    instructeur_emails = []
    if request.user.is_cerbere_user():
        try:
            client = SIAPClient.get_instance()
            operation = client.get_operation(
                user_login=request.user.cerbere_login,
                habilitation_id=request.session["habilitation_id"],
                operation_identifier=convention.programme.numero_operation,
            )
            if (
                "gestionnaireSecondaire" in operation
                and "utilisateurs" in operation["gestionnaireSecondaire"]
            ):
                for utilisateur in operation["gestionnaireSecondaire"]["utilisateurs"]:
                    # Keep only the instructeur's emails
                    if GroupProfile.SIAP_SER_GEST in [
                        group["profil"]["code"]
                        for group in utilisateur["groupes"]
                        if "profil" in group and "code" in group["profil"]
                    ]:
                        instructeur_emails.append(utilisateur["email"])
            user_to_remove = User.objects.filter(
                email__in=instructeur_emails,
                preferences_email=EmailPreferences.AUCUN,
            )
            instructeur_emails = [
                email
                for email in instructeur_emails
                if email not in [user.email for user in user_to_remove]
            ]
        except SIAPException:
            submitted = utils.ReturnStatus.WARNING
    else:
        instructeur_emails = convention.get_email_instructeur_users(
            include_partial=True
        )
    return instructeur_emails, submitted


def send_email_instruction(convention_url, convention, user, instructeur_emails):
    """
    Send email "convention à instruire" when bailleur submit the convention
    Send an email to the bailleur who click and bailleur TOUS
    Send an email to all instructeur (except the ones who select AUCUN as email preference)
    """
    # Send a confirmation email to bailleur
    email_data = {
        "convention_url": convention_url,
        "convention": str(convention),
        "bailleur": str(convention.bailleur.nom),
        "user": str(user),
    }

    if len(destinataires_bailleur := convention.get_email_bailleur_users()) > 0:
        email_service_to_bailleur = EmailService(
            to_emails=destinataires_bailleur,
            email_template_id=(
                EmailTemplateID.B_AVENANT_A_INSTRUIRE_CONFIRMATION
                if convention.is_avenant()
                else EmailTemplateID.B_CONVENTION_A_INSTRUIRE_CONFIRMATION
            ),
        )
        email_service_to_bailleur.send_transactional_email(email_data=email_data)

    # Send a notification email to instructeur
    if len(instructeur_emails) > 0:
        email_service_to_instructeur = EmailService(
            to_emails=instructeur_emails,
            email_template_id=(
                EmailTemplateID.BtoI_AVENANT_A_INSTRUIRE
                if convention.is_avenant()
                else EmailTemplateID.BtoI_CONVENTION_A_INSTRUIRE
            ),
        )
        email_service_to_instructeur.send_transactional_email(email_data=email_data)


def convention_feedback(request: HttpRequest, convention: Convention):
    notification_form = NotificationForm(request.POST)
    if notification_form.is_valid():
        cc = [request.user.email] if notification_form.cleaned_data["send_copy"] else []
        send_email_correction(
            request.build_absolute_uri(
                reverse("conventions:recapitulatif", args=[convention.uuid]),
            ),
            convention,
            request.user,
            cc,
            notification_form.cleaned_data["from_instructeur"],
            notification_form.cleaned_data["comment"],
            all_bailleur_users=(notification_form.cleaned_data["all_bailleur_users"]),
        )
        target_status = ConventionStatut.INSTRUCTION.label
        if notification_form.cleaned_data["from_instructeur"]:
            target_status = ConventionStatut.CORRECTION.label
        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=target_status,
            statut_convention_precedent=convention.statut,
            user=request.user,
            commentaire=notification_form.cleaned_data["comment"],
        ).save()
        convention.statut = target_status
        convention.save()

        return {
            "success": utils.ReturnStatus.SUCCESS,
            "convention": convention,
            "redirect": "recapitulatif",
        }
    return {
        **utils.base_convention_response_error(request, convention),
        "notificationForm": notification_form,
    }


def send_email_correction(
    convention_url,
    convention,
    user,
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
        if convention.is_avenant():
            email_template_id = EmailTemplateID.ItoB_AVENANT_CORRECTIONS_REQUISES
        else:
            email_template_id = EmailTemplateID.ItoB_CONVENTION_CORRECTIONS_REQUISES

    else:
        # Get instructeurs list following email preferences and interaction with the convention
        to = convention.get_email_instructeur_users()
        if convention.is_avenant():
            email_template_id = EmailTemplateID.BtoI_AVENANT_CORRECTIONS_FAITES
        else:
            email_template_id = EmailTemplateID.BtoI_CONVENTION_CORRECTIONS_FAITES

    # Send a confirmation email to bailleur
    if len(to) > 0:
        email_service_to_bailleur = EmailService(
            to_emails=to,
            cc_emails=cc,
            email_template_id=email_template_id,
        )
        email_service_to_bailleur.send_transactional_email(
            email_data={
                "convention_url": convention_url,
                "convention": str(convention),
                "user": str(user),
                "bailleur": str(convention.bailleur.nom),
                "commentaire": comment,
            },
        )


def convention_validate(request: HttpRequest, convention: Convention):
    convention_number_form = ConventionNumberForm(request.POST)
    complete_for_avenant_form = CompleteforavenantForm(request.POST, request.FILES)
    is_completeform = request.POST.get("completeform", False)
    is_finalisationform = request.POST.get("finalisationform", False)
    if is_completeform:
        if complete_for_avenant_form.is_valid():
            parentconvention = convention.parent
            programme = convention.programme
            parent_programme = parentconvention.programme
            if complete_for_avenant_form.cleaned_data["ville"]:
                parent_programme.ville = complete_for_avenant_form.cleaned_data["ville"]
                parent_programme.save()
                if not programme.ville:
                    programme.ville = complete_for_avenant_form.cleaned_data["ville"]
                    programme.save()

            lot = convention.lot
            parent_lot = parentconvention.lot
            if complete_for_avenant_form.cleaned_data["nb_logements"]:
                parent_lot.nb_logements = complete_for_avenant_form.cleaned_data[
                    "nb_logements"
                ]
                parent_lot.save()
                if not lot.nb_logements:
                    lot.nb_logements = complete_for_avenant_form.cleaned_data[
                        "nb_logements"
                    ]
                    lot.save()

            conventionfile = request.FILES.get("nom_fichier_signe", False)
            if conventionfile:
                ConventionFileService.upload_convention_file(
                    parentconvention, conventionfile
                )
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
            }
    else:
        if not is_finalisationform:
            convention_number_form.convention = convention
            if convention_number_form.is_valid():
                convention.numero = convention_number_form.cleaned_data[
                    "convention_numero"
                ]
                convention.save()
        if is_finalisationform or convention_number_form.is_valid():
            # Generate the doc should be placed after the status update
            # because the watermark report the status of the convention
            previous_status = convention.statut
            convention.statut = ConventionStatut.A_SIGNER.label
            ConventionHistory.objects.create(
                convention=convention,
                statut_convention=ConventionStatut.A_SIGNER.label,
                statut_convention_precedent=previous_status,
                user=request.user,
            ).save()
            if not convention.valide_le:
                convention.valide_le = datetime.date.today()
            convention.save()

            task_generate_and_send.delay(
                convention_uuid=str(convention.uuid),
                convention_url=request.build_absolute_uri(
                    reverse("conventions:preview", args=[convention.uuid])
                ),
                convention_email_validator=request.user.email,
            )

            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
            }

    convention_type1_and_2_form = ConventionType1and2Form(request.POST)
    opened_comments = Comment.objects.filter(
        convention=convention,
        statut=CommentStatut.OUVERT,
    ).order_by("cree_le")

    return {
        **utils.base_convention_response_error(request, convention),
        "notificationForm": NotificationForm(),
        "conventionNumberForm": convention_number_form,
        "complete_for_avenant_form": complete_for_avenant_form,
        "opened_comments": opened_comments,
        "ConventionType1and2Form": convention_type1_and_2_form,
    }


def convention_denonciation_validate(convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    parent = convention.parent
    date_denonciation = convention.date_denonciation
    parent.statut = ConventionStatut.DENONCEE.label
    parent.date_denonciation = date_denonciation
    parent.save()
    parent.avenants.all().update(
        statut=ConventionStatut.DENONCEE.label, date_denonciation=date_denonciation
    )
    result_status = utils.ReturnStatus.SUCCESS
    return {
        "success": result_status,
        "convention": convention,
    }


def convention_resiliation_validate(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    parent = convention.parent
    date_resiliation = convention.date_resiliation
    parent.statut = ConventionStatut.RESILIEE.label
    parent.date_resiliation = date_resiliation
    parent.save()
    parent.avenants.all().update(
        statut=ConventionStatut.RESILIEE.label,
        date_resiliation=date_resiliation,
    )
    result_status = utils.ReturnStatus.SUCCESS
    return {
        "success": result_status,
        "convention": convention,
    }


# FIXME to be tested
class ConventionSentService(ConventionService):
    # convention: Convention
    # request: HttpRequest
    # upform: UploadForm = UploadForm()
    # return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        upform = UploadForm()
        return {
            "convention": self.convention,
            "upform": upform,
            "extra_forms": {
                "upform": upform,
            },
        }

    def save(self):
        upform = UploadForm(self.request.POST, self.request.FILES)
        if upform.is_valid():
            ConventionFileService.upload_convention_file(
                self.convention, self.request.FILES["file"], update_statut=False
            )
            self.return_status = utils.ReturnStatus.SUCCESS
        return {
            "success": self.return_status,
            "convention": self.convention,
            "upform": upform,
            "extra_forms": {
                "upform": upform,
            },
        }


class ConventionUploadSignedService(ConventionService):

    def __init__(
        self,
        convention: Convention,
        request: AuthenticatedHttpRequest,
        step_number: int = 1,
    ):
        super().__init__(convention, request)
        self.stepper = Stepper(
            steps=[
                "Prévisualiser le document",
                "Indiquer la date de signature",
            ]
        )
        self.step_number = step_number

    def get(self):
        return {
            "convention": self.convention,
            "signature_date_form": ConventionDateSignatureForm(
                initial={
                    "televersement_convention_signee_le": datetime.date.today().strftime(
                        "%Y-%m-%d"
                    )
                }
            ),
            "form_step": self.stepper.get_form_step(step_number=self.step_number),
        }

    def save(self):
        form = ConventionDateSignatureForm(self.request.POST)
        if form.is_valid():
            self.convention.televersement_convention_signee_le = form.cleaned_data[
                "televersement_convention_signee_le"
            ]
            self.convention.statut = ConventionStatut.SIGNEE.label
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS

        return {
            "success": self.return_status,
            "convention": self.convention,
            "form": form,
        }
