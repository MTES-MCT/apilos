from django.http import HttpRequest
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from comments.models import Comment, CommentStatut
from conventions.forms.convention_number import ConventionNumberForm
from conventions.forms.notification import NotificationForm
from conventions.forms.type1and2 import ConventionType1and2Form
from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from conventions.models.convention_history import ConventionHistory
from conventions.services import utils
from conventions.tasks import generate_and_send
from core.services import EmailService
from programmes.models import Annexe
from siap.siap_client.client import SIAPClient


def convention_summary(request: HttpRequest, convention: Convention):
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
        "bailleur": convention.programme.bailleur,
        "lot": convention.lot,
        "locaux_collectifs": convention.lot.locaux_collectifs.all(),
        "programme": convention.programme,
        "logement_edds": convention.programme.logementedds.all(),
        "logements": convention.lot.logements.all(),
        "stationnements": convention.lot.type_stationnements.all(),
        "reference_cadastrales": convention.programme.referencecadastrales.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
        "notificationForm": NotificationForm(),
        "conventionNumberForm": convention_number_form,
        "ConventionType1and2Form": convention_type1_and_2_form,
    }


def _save_convention_type(request: HttpRequest, convention: Convention):
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


@require_POST
def convention_submit(request: HttpRequest, convention: Convention):
    submitted = utils.ReturnStatus.WARNING
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
                operation_identifier=convention.programme.numero_galion,
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
def convention_delete(convention: Convention):
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


def convention_feedback(request: HttpRequest, convention: Convention):
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


def convention_validate(request: HttpRequest, convention: Convention):
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

    return {
        **utils.base_convention_response_error(request, convention),
        "bailleur": convention.programme.bailleur,
        "lot": convention.lot,
        "programme": convention.programme,
        "logement_edds": convention.programme.logementedds.all(),
        "logements": convention.lot.logements.all(),
        "stationnements": convention.lot.type_stationnements.all(),
        "reference_cadastrales": convention.programme.referencecadastrales.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
        "notificationForm": NotificationForm(),
        "conventionNumberForm": convention_number_form,
    }
