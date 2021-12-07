import datetime

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from programmes.models import (
    Annexe,
)
from conventions.models import Convention, ConventionHistory, ConventionStatut, Pret
from conventions.forms import (
    ConventionCommentForm,
    ConventionFinancementForm,
    ConventionNumberForm,
    NotificationForm,
    PretFormSet,
    UploadForm,
)
from . import utils
from . import upload_objects
from . import convention_generator


def conventions_index(request, infilter):
    infilter.update(request.user.convention_filter())
    conventions = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .filter(**infilter)
    )
    return conventions


def convention_financement(request, convention_uuid):
    convention = Convention.objects.prefetch_related("pret_set").get(
        uuid=convention_uuid
    )
    import_warnings = None
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("UpdateAtomic", False):
            return _convention_financement_atomic_update(request, convention)

        # When the user cliked on "Téléverser" button
        formset = PretFormSet(request.POST)
        form = ConventionFinancementForm(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():

                result = upload_objects.handle_uploaded_xlsx(
                    upform, request.FILES["file"], Pret, convention, "financement.xlsx"
                )
                if result["success"] != utils.ReturnStatus.ERROR:
                    formset = PretFormSet(initial=result["objects"])
                    import_warnings = result["import_warnings"]
        # When the user cliked on "Enregistrer et Suivant"
        else:
            upform = UploadForm()
            formset.convention = convention
            if formset.is_valid():
                form.prets = formset
                form.convention = convention
                if form.is_valid():
                    _save_convention_financement(form, convention)
                    _save_convention_financement_prets(formset, convention)
                    # All is OK -> Next:
                    return utils.base_response_success(convention)
    # When display the file for the first time
    else:
        request.user.check_perm("convention.view_convention", convention)
        initial = []
        prets = convention.pret_set.all()
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
        upform = UploadForm()
        formset = PretFormSet(initial=initial)
        form = ConventionFinancementForm(
            initial={
                "uuid": convention.uuid,
                "annee_fin_conventionnement": convention.date_fin_conventionnement.year
                if convention.date_fin_conventionnement is not None
                else None,
                "fond_propre": convention.fond_propre,
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "import_warnings": import_warnings,
        "form": form,
        "formset": formset,
        "upform": upform,
    }


def _convention_financement_atomic_update(request, convention):
    form = ConventionFinancementForm(
        {
            "uuid": convention.uuid,
            "fond_propre": request.POST.get("fond_propre", convention.fond_propre),
            "annee_fin_conventionnement": request.POST.get(
                "annee_fin_conventionnement", convention.date_fin_conventionnement.year
            ),
        }
    )

    formset = PretFormSet(request.POST)
    initformset = {
        "form-TOTAL_FORMS": request.POST.get("form-TOTAL_FORMS", len(formset)),
        "form-INITIAL_FORMS": request.POST.get("form-INITIAL_FORMS", len(formset)),
    }
    for idx, form_pret in enumerate(formset):
        pret = Pret.objects.get(uuid=form_pret["uuid"].value())
        initformset = {
            **initformset,
            f"form-{idx}-uuid": pret.uuid,
            f"form-{idx}-numero": utils.get_form_value(form_pret, pret, "numero"),
            f"form-{idx}-date_octroi": utils.get_form_value(
                form_pret, pret, "date_octroi"
            ),
            f"form-{idx}-duree": utils.get_form_value(form_pret, pret, "duree"),
            f"form-{idx}-montant": utils.get_form_value(form_pret, pret, "montant"),
            f"form-{idx}-preteur": utils.get_form_value(form_pret, pret, "preteur"),
            f"form-{idx}-autre": utils.get_form_value(form_pret, pret, "autre"),
        }
    formset = PretFormSet(initformset)
    formset.convention = convention

    if formset.is_valid():
        form.prets = formset
        form.convention = convention
        if form.is_valid():
            _save_convention_financement(form, convention)
            _save_convention_financement_prets(formset, convention)
            return utils.base_response_redirect_recap_success(convention)
    upform = UploadForm()
    return {
        **utils.base_convention_response_error(request, convention),
        "upform": upform,
        "form": form,
        "formset": formset,
    }


def _save_convention_financement(form, convention):
    convention.date_fin_conventionnement = datetime.date(
        form.cleaned_data["annee_fin_conventionnement"], 6, 30
    )
    convention.fond_propre = form.cleaned_data["fond_propre"]
    convention.save()


def _save_convention_financement_prets(formset, convention):
    obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], formset))
    obj_uuids = list(filter(None, obj_uuids1))
    convention.pret_set.exclude(uuid__in=obj_uuids).delete()
    for form_pret in formset:
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
                convention=convention,
                bailleur=convention.bailleur,
                numero=form_pret.cleaned_data["numero"],
                date_octroi=form_pret.cleaned_data["date_octroi"],
                duree=form_pret.cleaned_data["duree"],
                montant=form_pret.cleaned_data["montant"],
                preteur=form_pret.cleaned_data["preteur"],
                autre=form_pret.cleaned_data["autre"],
            )
        pret.save()


def convention_comments(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        form = ConventionCommentForm(request.POST)
        if form.is_valid():
            convention.comments = utils.set_files_and_text_field(
                form.cleaned_data["comments_files"],
                form.cleaned_data["comments"],
            )
            convention.save()
            # All is OK -> Next:
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
                "form": form,
            }
    else:
        request.user.check_perm("convention.view_convention", convention)
        form = ConventionCommentForm(
            initial={
                "uuid": convention.uuid,
                "comments": convention.comments,
                **utils.get_text_and_files_from_field("comments", convention.comments),
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
    }


def convention_summary(request, convention_uuid, convention_number_form=None):
    convention = (
        Convention.objects.prefetch_related("bailleur")
        .prefetch_related("programme")
        .prefetch_related("programme__referencecadastrale_set")
        .prefetch_related("programme__logementedd_set")
        .prefetch_related("lot")
        .prefetch_related("lot__typestationnement_set")
        .prefetch_related("lot__logement_set")
        .get(uuid=convention_uuid)
    )
    if convention_number_form is None:
        convention_number_form = ConventionNumberForm(
            initial={
                "prefixe_numero": convention.prefixe_numero(),
                "suffixe_numero": convention.suffixe_numero(),
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "bailleur": convention.bailleur,
        "lot": convention.lot,
        "programme": convention.programme,
        "logement_edds": convention.programme.logementedd_set.all(),
        "logements": convention.lot.logement_set.all(),
        "stationnements": convention.lot.typestationnement_set.all(),
        "reference_cadastrales": convention.programme.referencecadastrale_set.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
        "notificationForm": NotificationForm(),
        "conventionNumberForm": convention_number_form,
    }


def convention_submit(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    submitted = utils.ReturnStatus.WARNING
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("SubmitConvention", False):

            ConventionHistory.objects.create(
                bailleur=convention.bailleur,
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
            _send_email_instruction(request, convention)
            submitted = utils.ReturnStatus.SUCCESS
        return {
            "success": submitted,
            "convention": convention,
        }
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
    }


@require_GET
@login_required
def convention_delete(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.change_convention", convention)
    convention.delete()


def _send_email_instruction(request, convention):
    # envoi au bailleur
    convention_url = request.build_absolute_uri(
        reverse("conventions:recapitulatif", args=[convention.uuid])
    )
    from_email = "contact@apilos.beta.gouv.fr"

    # All bailleur users from convention
    to = convention.get_email_bailleur_users()
    text_content = render_to_string(
        "emails/bailleur_instruction.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )
    html_content = render_to_string(
        "emails/bailleur_instruction.html",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )

    msg = EmailMultiAlternatives(
        f"Convention à instruire ({convention})", text_content, from_email, to
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    # envoie à l'instructeur
    to = convention.get_email_instructeur_users()
    text_content = render_to_string(
        "emails/instructeur_instruction.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )
    html_content = render_to_string(
        "emails/instructeur_instruction.html",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )

    msg = EmailMultiAlternatives(
        f"Convention à instruire ({convention})", text_content, from_email, to
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@require_POST
def convention_feedback(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    notification_form = NotificationForm(request.POST)
    if notification_form.is_valid():
        _send_email_correction(request, convention, notification_form)

        ConventionHistory.objects.create(
            bailleur=convention.bailleur,
            convention=convention,
            statut_convention=ConventionStatut.CORRECTION,
            statut_convention_precedent=convention.statut,
            user=request.user,
            commentaire=notification_form.cleaned_data["comment"],
        ).save()
        if (
            convention.statut != ConventionStatut.CORRECTION
            and request.user.is_instructeur()
        ):
            convention.statut = ConventionStatut.CORRECTION
            convention.save()

        return utils.base_response_redirect_recap_success(convention)
    return {
        **utils.base_convention_response_error(request, convention),
        "notificationForm": notification_form,
    }


def _send_email_correction(request, convention, notification_form):
    convention_url = request.build_absolute_uri(
        reverse("conventions:recapitulatif", args=[convention.uuid])
    )
    if notification_form.cleaned_data["from_instructeur"]:
        # All bailleur users from convention
        to = convention.get_email_bailleur_users()
        subject = f"Convention à modifier ({convention})"
        template_label = "bailleur_correction_needed"
    else:
        last_notification_from_instructeur = (
            convention.get_last_instructeur_notification()
        )
        if last_notification_from_instructeur:
            to = [last_notification_from_instructeur.user.email]
        else:
            # All instructeur users from convention
            to = convention.get_email_instructeur_users()
        subject = f"Convention modifiée ({convention})"
        template_label = "instructeur_correction_done"

    from_email = "contact@apilos.beta.gouv.fr"
    text_content = render_to_string(
        f"emails/{template_label}.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
            "commentaire": notification_form.cleaned_data["comment"],
        },
    )
    html_content = render_to_string(
        f"emails/{template_label}.html",
        {
            "convention_url": convention_url,
            "convention": convention,
            "commentaire": notification_form.cleaned_data["comment"],
        },
    )
    cc = [request.user.email] if notification_form.cleaned_data["send_copy"] else []

    msg = EmailMultiAlternatives(subject, text_content, from_email, to, cc=cc)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@require_POST
def convention_validate(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    request.user.check_perm("convention.change_convention", convention)

    convention_number_form = ConventionNumberForm(request.POST)
    if convention_number_form.is_valid():
        prefix_numero = "/".join(
            list(
                filter(
                    None,
                    convention_number_form.cleaned_data["prefixe_numero"].split("/"),
                )
            )
        )
        convention.numero = "/".join(
            [
                prefix_numero,
                convention_number_form.cleaned_data["suffixe_numero"],
            ]
        )
        convention.save()

    if convention_number_form.is_valid() or request.POST.get("Force"):

        file_stream = convention_generator.generate_hlm(convention)
        local_pdf_path = convention_generator.generate_pdf(file_stream, convention)

        ConventionHistory.objects.create(
            bailleur=convention.bailleur,
            convention=convention,
            statut_convention=ConventionStatut.VALIDE,
            statut_convention_precedent=convention.statut,
            user=request.user,
        ).save()
        if not convention.valide_le:
            convention.valide_le = timezone.now()
        convention.statut = ConventionStatut.VALIDE
        convention.save()
        _send_email_valide(request, convention, local_pdf_path)
        return {
            "success": utils.ReturnStatus.SUCCESS,
            "convention": convention,
        }

    convention = (
        Convention.objects.prefetch_related("bailleur")
        .prefetch_related("programme")
        .prefetch_related("programme__referencecadastrale_set")
        .prefetch_related("programme__logementedd_set")
        .prefetch_related("lot")
        .prefetch_related("lot__typestationnement_set")
        .prefetch_related("lot__logement_set")
        .get(uuid=convention_uuid)
    )
    return {
        **utils.base_convention_response_error(request, convention),
        "bailleur": convention.bailleur,
        "lot": convention.lot,
        "programme": convention.programme,
        "logement_edds": convention.programme.logementedd_set.all(),
        "logements": convention.lot.logement_set.all(),
        "stationnements": convention.lot.typestationnement_set.all(),
        "reference_cadastrales": convention.programme.referencecadastrale_set.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
        "notificationForm": NotificationForm(),
        "conventionNumberForm": convention_number_form,
    }


def _send_email_valide(request, convention, local_pdf_path=None):

    extention = local_pdf_path.split(".")[-1]

    convention_url = request.build_absolute_uri(
        reverse("conventions:recapitulatif", args=[convention.uuid])
    )
    from_email = "contact@apilos.beta.gouv.fr"

    cc = [request.user.email]
    # All bailleur users from convention
    to = convention.get_email_bailleur_users()

    text_content = render_to_string(
        "emails/bailleur_valide.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )
    html_content = render_to_string(
        "emails/bailleur_valide.html",
        {
            "convention_url": convention_url,
            "convention": convention,
        },
    )

    msg = EmailMultiAlternatives(
        f"Convention validé ({convention})", text_content, from_email, to, cc=cc
    )
    msg.attach_alternative(html_content, "text/html")

    if local_pdf_path is not None:
        pdf_file_handler = default_storage.open(local_pdf_path, "rb")
        if extention == "pdf":
            msg.attach(f"{convention}.pdf", pdf_file_handler.read(), "application/pdf")
        if extention == "docx":
            msg.attach(
                f"{convention}.docx",
                pdf_file_handler.read(),
                "application/vnd.openxmlformats-officedocument.wordprocessingm",
            )
        pdf_file_handler.close()
        msg.content_subtype = "html"

    msg.send()


@require_POST
def generate_convention(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("bailleur")
        .prefetch_related("lot")
        .prefetch_related("lot__typestationnement_set")
        .prefetch_related("lot__logement_set")
        .prefetch_related("pret_set")
        .prefetch_related("programme")
        .prefetch_related("programme__administration")
        .prefetch_related("programme__logementedd_set")
        .prefetch_related("programme__referencecadastrale_set")
        .get(uuid=convention_uuid)
    )
    file_stream = convention_generator.generate_hlm(convention)
    return file_stream, f"{convention}"
