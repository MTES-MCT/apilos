from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_GET
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings

from programmes.models import (
    Programme,
    Lot,
    LogementEDD,
    ReferenceCadastrale,
)
from programmes.forms import (
    ProgrammeSelectionForm,
    ProgrammeForm,
    ProgrammeCadastralForm,
    ProgrammeEDDForm,
    LogementEDDFormSet,
    ReferenceCadastraleFormSet,
)
from conventions.models import Convention
from conventions.forms import (
    UploadForm,
)
from . import utils
from . import upload_objects


def select_programme_create(request):
    if request.method == "POST":
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            existing_programme = form.cleaned_data["existing_programme"]
            if existing_programme == "selection":
                lot = Lot.objects.get(uuid=form.cleaned_data["lot_uuid"])
                request.user.check_perm("convention.add_convention", lot)
            else:
                request.user.check_perm("convention.add_convention")
                programme = Programme.objects.create(
                    nom=form.cleaned_data["nom"],
                    code_postal=form.cleaned_data["code_postal"],
                    ville=form.cleaned_data["ville"],
                    bailleur_id=form.cleaned_data["bailleur"],
                )
                programme.save()
                lot = Lot.objects.create(
                    nb_logements=form.cleaned_data["nb_logements"],
                    financement=form.cleaned_data["financement"],
                    type_habitat=form.cleaned_data["type_habitat"],
                    programme=programme,
                    bailleur_id=form.cleaned_data["bailleur"],
                )
                lot.save()
            convention = Convention.objects.create(
                lot=lot,
                programme_id=lot.programme_id,
                bailleur_id=lot.bailleur_id,
                financement=lot.financement,
            )
            if existing_programme != "selection":
                _send_email_staff(request, convention)

            convention.save()
            # All is OK -> Next:
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
            }

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm(
            initial={
                "existing_programme": "selection",
            }
        )

    programmes = _conventions_selection(request)
    return {
        "success": utils.ReturnStatus.ERROR,
        "programmes": programmes,
        "form": form,
        "editable": request.user.has_perm("convention.add_convention"),
        "bailleurs": request.user.bailleurs(),
    }  # render(request, "conventions/selection.html", {'form': form, 'programmes': programmes})


def _send_email_staff(request, convention):
    # envoi d'un mail au staff APiLos lors de la création from scratch
    convention_url = request.build_absolute_uri(
        reverse("conventions:recapitulatif", args=[convention.uuid])
    )
    from_email = "contact@apilos.beta.gouv.fr"
    to = ("contact@apilos.beta.gouv.fr",)
    text_content = render_to_string(
        "emails/alert_create_convention.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
            "programme": convention.programme,
            "user": request.user,
        },
    )
    html_content = render_to_string(
        "emails/alert_create_convention.html",
        {
            "convention_url": convention_url,
            "convention": convention,
            "programme": convention.programme,
            "user": request.user,
        },
    )

    if to:
        msg = EmailMultiAlternatives(
            f"[{settings.ENVIRONMENT.upper()}] Nouvelle convention créée de zéro ({convention})",
            text_content,
            from_email,
            to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


def select_programme_update(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        #        if request.POST['convention_uuid'] is None:
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            lot = Lot.objects.get(uuid=form.cleaned_data["lot_uuid"])
            convention.lot = lot
            convention.programme_id = lot.programme_id
            convention.bailleur_id = lot.bailleur_id
            convention.financement = lot.financement
            convention.save()
            # All is OK -> Next:
            return utils.base_response_success(convention)
    # If this is a GET (or any other method) create the default form.
    else:
        request.user.check_perm("convention.view_convention", convention)
        form = ProgrammeSelectionForm(
            initial={
                "lot_uuid": str(convention.lot.uuid),
                "existing_programme": "selection",
            }
        )
    programmes = _conventions_selection(request)
    return {
        **utils.base_convention_response_error(request, convention),
        "programmes": programmes,
        "form": form,
    }


def programme_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .get(uuid=convention_uuid)
    )
    programme = convention.programme
    lot = convention.lot
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("redirect_to_recap", False):
            return _programme_atomic_update(request, convention, programme, lot)
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            _save_programme_and_lot(programme, lot, form)
            return utils.base_response_success(convention)
    # If this is a GET (or any other method) create the default form.
    else:
        request.user.check_perm("convention.view_convention", convention)
        form = ProgrammeForm(
            initial={
                "uuid": programme.uuid,
                "nom": programme.nom,
                "adresse": programme.adresse,
                "code_postal": programme.code_postal,
                "ville": programme.ville,
                "nb_logements": lot.nb_logements,
                "type_habitat": lot.type_habitat,
                "type_operation": programme.type_operation,
                "anru": programme.anru,
                "autres_locaux_hors_convention": programme.autres_locaux_hors_convention,
                "nb_locaux_commerciaux": programme.nb_locaux_commerciaux,
                "nb_bureaux": programme.nb_bureaux,
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
    }


def _programme_atomic_update(request, convention, programme, lot):
    form = ProgrammeForm(
        {
            "uuid": programme.uuid,
            "nb_logements": request.POST.get("nb_logements", lot.nb_logements),
            "type_habitat": request.POST.get("type_habitat", lot.type_habitat),
            **utils.build_partial_form(
                request,
                programme,
                [
                    "nom",
                    "adresse",
                    "code_postal",
                    "ville",
                    "type_operation",
                    "anru",
                    "autres_locaux_hors_convention",
                    "nb_locaux_commerciaux",
                    "nb_bureaux",
                ],
            ),
        }
    )
    if form.is_valid():
        _save_programme_and_lot(programme, lot, form)
        return utils.base_response_redirect_recap_success(convention)
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
    }


def _save_programme_and_lot(programme, lot, form):
    programme.nom = form.cleaned_data["nom"]
    programme.adresse = form.cleaned_data["adresse"]
    programme.code_postal = form.cleaned_data["code_postal"]
    programme.ville = form.cleaned_data["ville"]
    programme.type_operation = form.cleaned_data["type_operation"]
    programme.anru = form.cleaned_data["anru"]
    programme.autres_locaux_hors_convention = form.cleaned_data[
        "autres_locaux_hors_convention"
    ]
    programme.nb_locaux_commerciaux = form.cleaned_data["nb_locaux_commerciaux"]
    programme.nb_bureaux = form.cleaned_data["nb_bureaux"]
    programme.save()
    lot.nb_logements = form.cleaned_data["nb_logements"]
    lot.type_habitat = form.cleaned_data["type_habitat"]
    lot.save()


def programme_cadastral_update(request, convention_uuid):
    # pylint: disable=R0915
    convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("programme__referencecadastrale_set")
        .get(uuid=convention_uuid)
    )
    programme = convention.programme
    import_warnings = None
    editable_upload = request.POST.get("editable_upload", False)
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        # When the user cliked on "Téléverser" button
        if request.POST.get("Upload", False):
            form = ProgrammeCadastralForm(request.POST)
            formset, upform, import_warnings, editable_upload = _upload_cadastre(
                request, convention, import_warnings, editable_upload
            )
        # When the user cliked on "Enregistrer et Suivant"
        else:
            result = _programme_cadastrale_atomic_update(request, convention, programme)
            if result["success"] == utils.ReturnStatus.SUCCESS and request.POST.get(
                "redirect_to_recap", False
            ):
                result["redirect"] = "recapitulatif"
            return {
                **result,
                "editable_upload": request.user.full_editable_convention(convention)
                or editable_upload,
            }
    # When display the file for the first time
    else:
        request.user.check_perm("convention.view_convention", convention)
        initial = []
        referencecadastrales = programme.referencecadastrale_set.all().order_by(
            "section"
        )
        for referencecadastrale in referencecadastrales:
            initial.append(
                {
                    "uuid": referencecadastrale.uuid,
                    "section": referencecadastrale.section,
                    "numero": referencecadastrale.numero,
                    "lieudit": referencecadastrale.lieudit,
                    "surface": referencecadastrale.surface,
                }
            )
        formset = ReferenceCadastraleFormSet(initial=initial)
        upform = UploadForm()
        form = ProgrammeCadastralForm(
            initial={
                "uuid": programme.uuid,
                "permis_construire": programme.permis_construire,
                "date_acte_notarie": utils.format_date_for_form(
                    programme.date_acte_notarie
                ),
                "date_achevement_previsible": utils.format_date_for_form(
                    programme.date_achevement_previsible
                ),
                "date_achat": utils.format_date_for_form(programme.date_achat),
                "date_achevement": utils.format_date_for_form(
                    programme.date_achevement
                ),
                **utils.get_text_and_files_from_field("vendeur", programme.vendeur),
                **utils.get_text_and_files_from_field("acquereur", programme.acquereur),
                **utils.get_text_and_files_from_field(
                    "reference_notaire", programme.reference_notaire
                ),
                **utils.get_text_and_files_from_field(
                    "reference_publication_acte", programme.reference_publication_acte
                ),
                **utils.get_text_and_files_from_field(
                    "acte_de_propriete", programme.acte_de_propriete
                ),
                **utils.get_text_and_files_from_field(
                    "acte_notarial", programme.acte_notarial
                ),
                **utils.get_text_and_files_from_field(
                    "reference_cadastrale", programme.reference_cadastrale
                ),
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
        "editable_upload": request.user.full_editable_convention(convention)
        or editable_upload,
    }


def _upload_cadastre(request, convention, import_warnings, editable_upload):
    formset = ReferenceCadastraleFormSet(request.POST)
    upform = UploadForm(request.POST, request.FILES)
    if upform.is_valid():
        result = upload_objects.handle_uploaded_xlsx(
            upform,
            request.FILES["file"],
            ReferenceCadastrale,
            convention,
            "cadastre.xlsx",
        )
        if result["success"] != utils.ReturnStatus.ERROR:
            refcads_by_section = {}
            for refcad in ReferenceCadastrale.objects.filter(
                programme_id=convention.programme_id
            ):
                refcads_by_section[refcad.section] = refcad.uuid

            for obj in result["objects"]:
                if "section" in obj and obj["section"] in refcads_by_section:
                    obj["uuid"] = refcads_by_section[obj["section"]]

            formset = ReferenceCadastraleFormSet(initial=result["objects"])
            import_warnings = result["import_warnings"]
            editable_upload = True
    return formset, upform, import_warnings, editable_upload


def _save_programme_cadastrale(form, programme):
    programme.permis_construire = form.cleaned_data["permis_construire"]
    programme.date_acte_notarie = form.cleaned_data["date_acte_notarie"]
    programme.date_achevement_previsible = form.cleaned_data[
        "date_achevement_previsible"
    ]
    programme.date_achat = form.cleaned_data["date_achat"]
    programme.date_achevement = form.cleaned_data["date_achevement"]
    programme.vendeur = utils.set_files_and_text_field(
        form.cleaned_data["vendeur_files"],
        form.cleaned_data["vendeur"],
    )
    programme.acquereur = utils.set_files_and_text_field(
        form.cleaned_data["acquereur_files"],
        form.cleaned_data["acquereur"],
    )
    programme.reference_notaire = utils.set_files_and_text_field(
        form.cleaned_data["reference_notaire_files"],
        form.cleaned_data["reference_notaire"],
    )
    programme.reference_publication_acte = utils.set_files_and_text_field(
        form.cleaned_data["reference_publication_acte_files"],
        form.cleaned_data["reference_publication_acte"],
    )
    programme.acte_de_propriete = utils.set_files_and_text_field(
        form.cleaned_data["acte_de_propriete_files"],
    )
    programme.acte_notarial = utils.set_files_and_text_field(
        form.cleaned_data["acte_notarial_files"],
    )
    programme.reference_cadastrale = utils.set_files_and_text_field(
        form.cleaned_data["reference_cadastrale_files"],
    )
    programme.save()


def _save_programme_reference_cadastrale(formset, convention, programme):
    obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], formset))
    obj_uuids = list(filter(None, obj_uuids1))
    programme.referencecadastrale_set.exclude(uuid__in=obj_uuids).delete()
    for form in formset:
        if form.cleaned_data["uuid"]:
            reference_cadastrale = ReferenceCadastrale.objects.get(
                uuid=form.cleaned_data["uuid"]
            )
            reference_cadastrale.section = form.cleaned_data["section"]
            reference_cadastrale.numero = form.cleaned_data["numero"]
            reference_cadastrale.lieudit = form.cleaned_data["lieudit"]
            reference_cadastrale.surface = form.cleaned_data["surface"]
        else:
            reference_cadastrale = ReferenceCadastrale.objects.create(
                programme=programme,
                bailleur=convention.bailleur,
                section=form.cleaned_data["section"],
                numero=form.cleaned_data["numero"],
                lieudit=form.cleaned_data["lieudit"],
                surface=form.cleaned_data["surface"],
            )
        reference_cadastrale.save()


def _programme_cadastrale_atomic_update(request, convention, programme):
    form = ProgrammeCadastralForm(
        {
            "uuid": programme.uuid,
            **utils.build_partial_form(
                request,
                programme,
                [
                    "permis_construire",
                    "date_acte_notarie",
                    "date_achevement_previsible",
                    "date_achat",
                    "date_achevement",
                ],
            ),
            **utils.build_partial_text_and_files_form(
                request,
                programme,
                [
                    "vendeur",
                    "acquereur",
                    "reference_notaire",
                    "reference_publication_acte",
                    "acte_de_propriete",
                    "acte_notarial",
                    "reference_cadastrale",
                ],
            ),
        }
    )
    form_is_valid = form.is_valid()

    formset = ReferenceCadastraleFormSet(request.POST)
    initformset = {
        "form-TOTAL_FORMS": request.POST.get("form-TOTAL_FORMS", len(formset)),
        "form-INITIAL_FORMS": request.POST.get("form-INITIAL_FORMS", len(formset)),
    }
    for idx, form_reference_cadastrale in enumerate(formset):
        if form_reference_cadastrale["uuid"].value():
            reference_cadastrale = ReferenceCadastrale.objects.get(
                uuid=form_reference_cadastrale["uuid"].value()
            )
            initformset = {
                **initformset,
                f"form-{idx}-uuid": reference_cadastrale.uuid,
                f"form-{idx}-section": utils.get_form_value(
                    form_reference_cadastrale, reference_cadastrale, "section"
                ),
                f"form-{idx}-numero": utils.get_form_value(
                    form_reference_cadastrale, reference_cadastrale, "numero"
                ),
                f"form-{idx}-lieudit": utils.get_form_value(
                    form_reference_cadastrale, reference_cadastrale, "lieudit"
                ),
                f"form-{idx}-surface": utils.get_form_value(
                    form_reference_cadastrale, reference_cadastrale, "surface"
                ),
            }
        else:
            initformset = {
                **initformset,
                f"form-{idx}-section": form_reference_cadastrale["section"].value(),
                f"form-{idx}-numero": form_reference_cadastrale["numero"].value(),
                f"form-{idx}-lieudit": form_reference_cadastrale["lieudit"].value(),
                f"form-{idx}-surface": form_reference_cadastrale["surface"].value(),
            }
    formset = ReferenceCadastraleFormSet(initformset)
    formset_is_valid = formset.is_valid()

    if form_is_valid and formset_is_valid:
        _save_programme_cadastrale(form, programme)
        _save_programme_reference_cadastrale(formset, convention, programme)
        return {
            "success": utils.ReturnStatus.SUCCESS,
            "convention": convention,
        }
    upform = UploadForm()
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
        "formset": formset,
        "upform": upform,
    }


def programme_edd_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .prefetch_related("programme__logementedd_set")
        .get(uuid=convention_uuid)
    )
    programme = convention.programme
    import_warnings = None
    editable_upload = request.POST.get("editable_upload", False)
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        # When the user cliked on "Téléverser" button
        if request.POST.get("Upload", False):
            form = ProgrammeEDDForm(request.POST)
            formset, upform, import_warnings, editable_upload = _upload_logements_edd(
                request, convention, import_warnings, editable_upload
            )
        # When the user cliked on "Enregistrer et Suivant"
        else:
            result = _programme_edd_atomic_update(request, convention, programme)
            if result["success"] == utils.ReturnStatus.SUCCESS and request.POST.get(
                "redirect_to_recap", False
            ):
                result["redirect"] = "recapitulatif"
            return {
                **result,
                "editable_upload": request.user.full_editable_convention(convention)
                or request.POST.get("redirect_to_recap", False),
            }
    # When display the file for the first time
    else:
        request.user.check_perm("convention.view_convention", convention)
        initial = []
        for logementedd in programme.logementedd_set.all():
            initial.append(
                {
                    "uuid": logementedd.uuid,
                    "financement": logementedd.financement,
                    "designation": logementedd.designation,
                    "typologie": logementedd.typologie,
                }
            )
        formset = LogementEDDFormSet(initial=initial)
        upform = UploadForm()
        form = ProgrammeEDDForm(
            initial={
                "uuid": programme.uuid,
                "lot_uuid": convention.lot.uuid,
                **utils.get_text_and_files_from_field(
                    "edd_volumetrique", convention.lot.edd_volumetrique
                ),
                "mention_publication_edd_volumetrique": (
                    programme.mention_publication_edd_volumetrique
                ),
                **utils.get_text_and_files_from_field(
                    "edd_classique", convention.lot.edd_classique
                ),
                "mention_publication_edd_classique": programme.mention_publication_edd_classique,
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
        "editable_upload": request.user.full_editable_convention(convention)
        or editable_upload,
    }


def _upload_logements_edd(request, convention, import_warnings, editable_upload):
    formset = LogementEDDFormSet(request.POST)
    upform = UploadForm(request.POST, request.FILES)
    if upform.is_valid():
        result = upload_objects.handle_uploaded_xlsx(
            upform,
            request.FILES["file"],
            LogementEDD,
            convention,
            "logements_edd.xlsx",
        )
        if result["success"] != utils.ReturnStatus.ERROR:
            edd_lgts_by_designation = {}
            for edd_lgt in LogementEDD.objects.filter(
                programme_id=convention.programme_id
            ):
                edd_lgts_by_designation[edd_lgt.designation] = edd_lgt.uuid

            for obj in result["objects"]:
                if (
                    "designation" in obj
                    and obj["designation"] in edd_lgts_by_designation
                ):
                    obj["uuid"] = edd_lgts_by_designation[obj["designation"]]

            formset = LogementEDDFormSet(initial=result["objects"])
            import_warnings = result["import_warnings"]
            editable_upload = True
    return formset, upform, import_warnings, editable_upload


def _programme_edd_atomic_update(request, convention, programme):
    form = ProgrammeEDDForm(
        {
            "uuid": programme.uuid,
            **utils.init_text_and_files_from_field(
                request, convention.lot, "edd_volumetrique"
            ),
            "mention_publication_edd_volumetrique": (
                request.POST.get(
                    "mention_publication_edd_volumetrique",
                    programme.mention_publication_edd_volumetrique,
                )
            ),
            **utils.init_text_and_files_from_field(
                request, convention.lot, "edd_classique"
            ),
            "mention_publication_edd_classique": (
                request.POST.get(
                    "mention_publication_edd_classique",
                    programme.mention_publication_edd_classique,
                )
            ),
        }
    )
    form_is_valid = form.is_valid()

    formset = LogementEDDFormSet(request.POST)
    initformset = {
        "form-TOTAL_FORMS": request.POST.get("form-TOTAL_FORMS", len(formset)),
        "form-INITIAL_FORMS": request.POST.get("form-INITIAL_FORMS", len(formset)),
    }
    for idx, form_logementedd in enumerate(formset):
        if form_logementedd["uuid"].value():
            logementedd = LogementEDD.objects.get(uuid=form_logementedd["uuid"].value())
            initformset = {
                **initformset,
                f"form-{idx}-uuid": logementedd.uuid,
                f"form-{idx}-designation": utils.get_form_value(
                    form_logementedd, logementedd, "designation"
                ),
                f"form-{idx}-financement": utils.get_form_value(
                    form_logementedd, logementedd, "financement"
                ),
                f"form-{idx}-typologie": utils.get_form_value(
                    form_logementedd, logementedd, "typologie"
                ),
            }
        else:
            initformset = {
                **initformset,
                f"form-{idx}-designation": form_logementedd["designation"].value(),
                f"form-{idx}-financement": form_logementedd["financement"].value(),
                f"form-{idx}-typologie": form_logementedd["typologie"].value(),
            }
    formset = LogementEDDFormSet(initformset)
    formset.programme_id = convention.programme_id
    formset.ignore_optional_errors = request.POST.get("ignore_optional_errors", False)
    formset_is_valid = formset.is_valid()

    if form_is_valid and formset_is_valid:
        _save_programme_edd(form, programme, convention.lot)
        _save_programme_logement_edd(formset, convention, programme)
        return {
            "success": utils.ReturnStatus.SUCCESS,
            "convention": convention,
        }
    upform = UploadForm()
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
        "formset": formset,
        "upform": upform,
    }


def _save_programme_edd(form, programme, lot):
    lot.edd_volumetrique = utils.set_files_and_text_field(
        form.cleaned_data["edd_volumetrique_files"],
        form.cleaned_data["edd_volumetrique"],
    )
    programme.mention_publication_edd_volumetrique = form.cleaned_data[
        "mention_publication_edd_volumetrique"
    ]
    lot.edd_classique = utils.set_files_and_text_field(
        form.cleaned_data["edd_classique_files"],
        form.cleaned_data["edd_classique"],
    )
    programme.mention_publication_edd_classique = form.cleaned_data[
        "mention_publication_edd_classique"
    ]
    lot.save()
    programme.save()


def _save_programme_logement_edd(formset, convention, programme):
    lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], formset))
    lgt_uuids = list(filter(None, lgt_uuids1))
    programme.logementedd_set.exclude(uuid__in=lgt_uuids).delete()
    for form_logementedd in formset:
        if form_logementedd.cleaned_data["uuid"]:
            logementedd = LogementEDD.objects.get(
                uuid=form_logementedd.cleaned_data["uuid"]
            )
            logementedd.financement = form_logementedd.cleaned_data["financement"]
            logementedd.designation = form_logementedd.cleaned_data["designation"]
            logementedd.typologie = form_logementedd.cleaned_data["typologie"]
        else:
            logementedd = LogementEDD.objects.create(
                programme=programme,
                bailleur=convention.bailleur,
                financement=form_logementedd.cleaned_data["financement"],
                designation=form_logementedd.cleaned_data["designation"],
                typologie=form_logementedd.cleaned_data["typologie"],
            )
        logementedd.save()


def _conventions_selection(request):
    return (
        request.user.lots()
        .prefetch_related("programme")
        .prefetch_related("convention_set")
        .order_by("programme__ville", "programme__nom", "nb_logements", "financement")
    )


@require_GET
def display_operation(request, programme_uuid, financement):
    # CONVENTION
    try:
        programme = request.user.programmes().get(uuid=programme_uuid)
    except Programme.DoesNotExist as does_not_exist:
        raise PermissionDenied from does_not_exist

    try:
        convention = request.user.conventions().get(
            programme=programme,
            financement=financement,
        )
        return {"success": utils.ReturnStatus.SUCCESS, "convention": convention}
    except Convention.DoesNotExist:
        # LOT case
        lot = Lot.objects.get(
            programme=programme,
            financement=financement,
        )
        form = ProgrammeSelectionForm(
            initial={"existing_programme": "selection", "lot_uuid": f"{lot.uuid}"}
        )

        programmes = _conventions_selection(request)
        return {
            "success": utils.ReturnStatus.WARNING,
            "programmes": programmes,
            "form": form,
            "editable": request.user.has_perm("convention.add_convention"),
            "bailleurs": request.user.bailleurs(),
        }
