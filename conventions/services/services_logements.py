from programmes.models import (
    Logement,
    Annexe,
    TypeStationnement,
)
from programmes.forms import (
    LogementFormSet,
    TypeStationnementFormSet,
    AnnexeFormSet,
    LotAnnexeForm,
)
from conventions.models import Convention
from conventions.forms import (
    UploadForm,
)
from . import utils
from . import upload_objects


def logements_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__logement_set")
        .get(uuid=convention_uuid)
    )
    import_warnings = None
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("UpdateAtomic", False):
            return _logements_atomic_update(request, convention)

        # When the user cliked on "Téléverser" button
        formset = LogementFormSet(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():

                result = upload_objects.handle_uploaded_xlsx(
                    upform,
                    request.FILES["file"],
                    Logement,
                    convention,
                    "logements.xlsx",
                )
                if result["success"] != utils.ReturnStatus.ERROR:
                    formset = LogementFormSet(initial=result["objects"])
                    import_warnings = result["import_warnings"]
        # When the user cliked on "Enregistrer et Suivant"
        else:
            upform = UploadForm()
            formset.programme_id = convention.programme_id
            formset.lot_id = convention.lot_id
            if formset.is_valid():
                _save_logements(formset, convention)
                # All is OK -> Next:
                return utils.base_response_redirect_recap_success(convention)
    # When display the file for the first time
    else:
        request.user.check_perm("convention.view_convention", convention)
        initial = []
        logements = convention.lot.logement_set.all()
        for logement in logements:
            initial.append(
                {
                    "uuid": logement.uuid,
                    "designation": logement.designation,
                    "typologie": logement.typologie,
                    "surface_habitable": logement.surface_habitable,
                    "surface_annexes": logement.surface_annexes,
                    "surface_annexes_retenue": logement.surface_annexes_retenue,
                    "surface_utile": logement.surface_utile,
                    "loyer_par_metre_carre": logement.loyer_par_metre_carre,
                    "coeficient": logement.coeficient,
                    "loyer": logement.loyer,
                }
            )
        upform = UploadForm()
        formset = LogementFormSet(initial=initial)
    return {
        **utils.base_convention_response_error(request, convention),
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def _logements_atomic_update(request, convention):
    formset = LogementFormSet(request.POST)
    initformset = {
        "form-TOTAL_FORMS": request.POST.get("form-TOTAL_FORMS", len(formset)),
        "form-INITIAL_FORMS": request.POST.get("form-INITIAL_FORMS", len(formset)),
    }
    for idx, form_logement in enumerate(formset):
        logement = Logement.objects.get(uuid=form_logement["uuid"].value())
        initformset = {
            **initformset,
            f"form-{idx}-uuid": logement.uuid,
            f"form-{idx}-designation": utils.get_form_value(
                form_logement, logement, "designation"
            ),
            f"form-{idx}-typologie": utils.get_form_value(
                form_logement, logement, "typologie"
            ),
            f"form-{idx}-surface_habitable": utils.get_form_value(
                form_logement, logement, "surface_habitable"
            ),
            f"form-{idx}-surface_annexes": utils.get_form_value(
                form_logement, logement, "surface_annexes"
            ),
            f"form-{idx}-surface_annexes_retenue": utils.get_form_value(
                form_logement, logement, "surface_annexes_retenue"
            ),
            f"form-{idx}-surface_utile": utils.get_form_value(
                form_logement, logement, "surface_utile"
            ),
            f"form-{idx}-loyer_par_metre_carre": utils.get_form_value(
                form_logement, logement, "loyer_par_metre_carre"
            ),
            f"form-{idx}-coeficient": utils.get_form_value(
                form_logement, logement, "coeficient"
            ),
            f"form-{idx}-loyer": utils.get_form_value(form_logement, logement, "loyer"),
        }
    formset = LogementFormSet(initformset)
    formset.programme_id = convention.programme_id
    formset.lot_id = convention.lot_id

    if formset.is_valid():
        _save_logements(formset, convention)
        return utils.base_response_redirect_recap_success(convention)
    return {
        **utils.base_convention_response_error(request, convention),
        "formset": formset,
        "upform": UploadForm(),
    }


def _save_logements(formset, convention):
    lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], formset))
    lgt_uuids = list(filter(None, lgt_uuids1))
    convention.lot.logement_set.exclude(uuid__in=lgt_uuids).delete()
    for form_logement in formset:
        if form_logement.cleaned_data["uuid"]:
            logement = Logement.objects.get(uuid=form_logement.cleaned_data["uuid"])
            logement.designation = form_logement.cleaned_data["designation"]
            logement.typologie = form_logement.cleaned_data["typologie"]
            logement.surface_habitable = form_logement.cleaned_data["surface_habitable"]
            logement.surface_annexes = form_logement.cleaned_data["surface_annexes"]
            logement.surface_annexes_retenue = form_logement.cleaned_data[
                "surface_annexes_retenue"
            ]
            logement.surface_utile = form_logement.cleaned_data["surface_utile"]
            logement.loyer_par_metre_carre = form_logement.cleaned_data[
                "loyer_par_metre_carre"
            ]
            logement.coeficient = form_logement.cleaned_data["coeficient"]
            logement.loyer = form_logement.cleaned_data["loyer"]
        else:
            logement = Logement.objects.create(
                lot=convention.lot,
                bailleur=convention.bailleur,
                designation=form_logement.cleaned_data["designation"],
                typologie=form_logement.cleaned_data["typologie"],
                surface_habitable=form_logement.cleaned_data["surface_habitable"],
                surface_annexes=form_logement.cleaned_data["surface_annexes"],
                surface_annexes_retenue=form_logement.cleaned_data[
                    "surface_annexes_retenue"
                ],
                surface_utile=form_logement.cleaned_data["surface_utile"],
                loyer_par_metre_carre=form_logement.cleaned_data[
                    "loyer_par_metre_carre"
                ],
                coeficient=form_logement.cleaned_data["coeficient"],
                loyer=form_logement.cleaned_data["loyer"],
            )
        logement.save()


def annexes_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__logement_set")
        .prefetch_related("lot__logement_set__annexe_set")
        .get(uuid=convention_uuid)
    )
    import_warnings = None
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("UpdateAtomic", False):
            return _annexes_atomic_update(request, convention)
        # When the user cliked on "Téléverser" button
        formset = AnnexeFormSet(request.POST)
        form = LotAnnexeForm(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = upload_objects.handle_uploaded_xlsx(
                    upform, request.FILES["file"], Annexe, convention, "annexes.xlsx"
                )
                if result["success"] != utils.ReturnStatus.ERROR:
                    formset = AnnexeFormSet(initial=result["objects"])
                    import_warnings = result["import_warnings"]
        # When the user cliked on "Enregistrer et Suivant"
        else:
            upform = UploadForm()
            formset.convention = convention
            form_is_valid = form.is_valid()
            formset_is_valid = formset.is_valid()
            if form_is_valid and formset_is_valid:
                _save_lot_annexes(form, convention.lot)
                _save_annexes(formset, convention)
                return utils.base_response_success(convention)
    # When display the file for the first time
    else:
        request.user.check_perm("convention.view_convention", convention)
        initial = []
        annexes = Annexe.objects.filter(logement__lot_id=convention.lot.id)
        for annexe in annexes:
            initial.append(
                {
                    "uuid": annexe.uuid,
                    "typologie": annexe.typologie,
                    "logement_designation": annexe.logement.designation,
                    "logement_typologie": annexe.logement.typologie,
                    "surface_hors_surface_retenue": annexe.surface_hors_surface_retenue,
                    "loyer_par_metre_carre": annexe.loyer_par_metre_carre,
                    "loyer": annexe.loyer,
                }
            )
        upform = UploadForm()
        formset = AnnexeFormSet(initial=initial)
        form = LotAnnexeForm(
            initial={
                "uuid": convention.lot.uuid,
                "annexe_caves": convention.lot.annexe_caves,
                "annexe_soussols": convention.lot.annexe_soussols,
                "annexe_remises": convention.lot.annexe_remises,
                "annexe_ateliers": convention.lot.annexe_ateliers,
                "annexe_sechoirs": convention.lot.annexe_sechoirs,
                "annexe_celliers": convention.lot.annexe_celliers,
                "annexe_resserres": convention.lot.annexe_resserres,
                "annexe_combles": convention.lot.annexe_combles,
                "annexe_balcons": convention.lot.annexe_balcons,
                "annexe_loggias": convention.lot.annexe_loggias,
                "annexe_terrasses": convention.lot.annexe_terrasses,
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def _save_lot_annexes(form, lot):
    lot.annexe_caves = form.cleaned_data["annexe_caves"]
    lot.annexe_soussols = form.cleaned_data["annexe_soussols"]
    lot.annexe_remises = form.cleaned_data["annexe_remises"]
    lot.annexe_ateliers = form.cleaned_data["annexe_ateliers"]
    lot.annexe_sechoirs = form.cleaned_data["annexe_sechoirs"]
    lot.annexe_celliers = form.cleaned_data["annexe_celliers"]
    lot.annexe_resserres = form.cleaned_data["annexe_resserres"]
    lot.annexe_combles = form.cleaned_data["annexe_combles"]
    lot.annexe_balcons = form.cleaned_data["annexe_balcons"]
    lot.annexe_loggias = form.cleaned_data["annexe_loggias"]
    lot.annexe_terrasses = form.cleaned_data["annexe_terrasses"]
    lot.save()


def _annexes_atomic_update(request, convention):

    form = LotAnnexeForm(
        {
            "uuid": convention.lot.uuid,
            **utils.build_partial_form(
                request,
                convention.lot,
                [
                    "annexe_caves",
                    "annexe_soussols",
                    "annexe_remises",
                    "annexe_ateliers",
                    "annexe_sechoirs",
                    "annexe_celliers",
                    "annexe_resserres",
                    "annexe_combles",
                    "annexe_balcons",
                    "annexe_loggias",
                    "annexe_terrasses",
                ],
            ),
        }
    )
    form_is_valid = form.is_valid()

    formset = AnnexeFormSet(request.POST)
    initformset = {
        "form-TOTAL_FORMS": request.POST.get("form-TOTAL_FORMS", len(formset)),
        "form-INITIAL_FORMS": request.POST.get("form-INITIAL_FORMS", len(formset)),
    }
    for idx, form_annexe in enumerate(formset):
        annexe = Annexe.objects.get(uuid=form_annexe["uuid"].value())
        initformset = {
            **initformset,
            f"form-{idx}-uuid": annexe.uuid,
            f"form-{idx}-typologie": utils.get_form_value(
                form_annexe, annexe, "typologie"
            ),
            f"form-{idx}-logement_designation": (
                form_annexe["logement_designation"].value()
                if form_annexe["logement_designation"].value() is not None
                else annexe.logement.designation
            ),
            f"form-{idx}-logement_typologie": (
                form_annexe["logement_typologie"].value()
                if form_annexe["logement_typologie"].value() is not None
                else annexe.logement.typologie
            ),
            f"form-{idx}-surface_hors_surface_retenue": utils.get_form_value(
                form_annexe, annexe, "surface_hors_surface_retenue"
            ),
            f"form-{idx}-loyer_par_metre_carre": utils.get_form_value(
                form_annexe, annexe, "loyer_par_metre_carre"
            ),
            f"form-{idx}-loyer": utils.get_form_value(form_annexe, annexe, "loyer"),
        }
    formset = AnnexeFormSet(initformset)
    formset.convention = convention
    formset_is_valid = formset.is_valid()

    if form_is_valid and formset_is_valid:
        _save_lot_annexes(form, convention.lot)
        _save_annexes(formset, convention)
        return utils.base_response_redirect_recap_success(convention)
    return {
        **utils.base_convention_response_error(request, convention),
        "formset": formset,
        "upform": UploadForm(),
    }


def _save_annexes(formset, convention):
    obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], formset))
    obj_uuids = list(filter(None, obj_uuids1))
    Annexe.objects.filter(logement__lot_id=convention.lot.id).exclude(
        uuid__in=obj_uuids
    ).delete()
    for form_annexe in formset:
        if form_annexe.cleaned_data["uuid"]:
            annexe = Annexe.objects.get(uuid=form_annexe.cleaned_data["uuid"])
            logement = Logement.objects.get(
                designation=form_annexe.cleaned_data["logement_designation"],
                lot=convention.lot,
            )
            annexe.logement = logement
            annexe.typologie = form_annexe.cleaned_data["typologie"]
            annexe.surface_hors_surface_retenue = form_annexe.cleaned_data[
                "surface_hors_surface_retenue"
            ]
            annexe.loyer_par_metre_carre = form_annexe.cleaned_data[
                "loyer_par_metre_carre"
            ]
            annexe.loyer = form_annexe.cleaned_data["loyer"]
        else:
            logement = Logement.objects.get(
                designation=form_annexe.cleaned_data["logement_designation"],
                lot=convention.lot,
            )
            annexe = Annexe.objects.create(
                logement=logement,
                bailleur=convention.bailleur,
                typologie=form_annexe.cleaned_data["typologie"],
                surface_hors_surface_retenue=form_annexe.cleaned_data[
                    "surface_hors_surface_retenue"
                ],
                loyer_par_metre_carre=form_annexe.cleaned_data["loyer_par_metre_carre"],
                loyer=form_annexe.cleaned_data["loyer"],
            )
        annexe.save()


def stationnements_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__typestationnement_set")
        .get(uuid=convention_uuid)
    )
    import_warnings = None
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("UpdateAtomic", False):
            return _stationnements_atomic_update(request, convention)
        # When the user cliked on "Téléverser" button
        formset = TypeStationnementFormSet(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():

                result = upload_objects.handle_uploaded_xlsx(
                    upform,
                    request.FILES["file"],
                    TypeStationnement,
                    convention,
                    "stationnements.xlsx",
                )
                if result["success"] != utils.ReturnStatus.ERROR:
                    formset = TypeStationnementFormSet(initial=result["objects"])
                    import_warnings = result["import_warnings"]
        # When the user cliked on "Enregistrer et Suivant"
        else:
            upform = UploadForm()
            if formset.is_valid():
                _save_stationnements(formset, convention)
                return utils.base_response_success(convention)
    # When display the file for the first time
    else:
        request.user.check_perm("convention.view_convention", convention)
        initial = []
        stationnements = convention.lot.typestationnement_set.all()
        for stationnement in stationnements:
            initial.append(
                {
                    "uuid": stationnement.uuid,
                    "typologie": stationnement.typologie,
                    "nb_stationnements": stationnement.nb_stationnements,
                    "loyer": stationnement.loyer,
                }
            )
        upform = UploadForm()
        formset = TypeStationnementFormSet(initial=initial)
    return {
        **utils.base_convention_response_error(request, convention),
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def _stationnements_atomic_update(request, convention):
    formset = TypeStationnementFormSet(request.POST)
    initformset = {
        "form-TOTAL_FORMS": request.POST.get("form-TOTAL_FORMS", len(formset)),
        "form-INITIAL_FORMS": request.POST.get("form-INITIAL_FORMS", len(formset)),
    }
    for idx, form_stationnement in enumerate(formset):
        stationnement = TypeStationnement.objects.get(
            uuid=form_stationnement["uuid"].value()
        )
        initformset = {
            **initformset,
            f"form-{idx}-uuid": stationnement.uuid,
            f"form-{idx}-typologie": utils.get_form_value(
                form_stationnement, stationnement, "typologie"
            ),
            f"form-{idx}-nb_stationnements": utils.get_form_value(
                form_stationnement, stationnement, "nb_stationnements"
            ),
            f"form-{idx}-loyer": utils.get_form_value(
                form_stationnement, stationnement, "loyer"
            ),
        }
    formset = TypeStationnementFormSet(initformset)
    if formset.is_valid():
        _save_stationnements(formset, convention)
        return utils.base_response_redirect_recap_success(convention)
    return {
        **utils.base_convention_response_error(request, convention),
        "formset": formset,
        "upform": UploadForm(),
    }


def _save_stationnements(formset, convention):
    obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], formset))
    obj_uuids = list(filter(None, obj_uuids1))
    Annexe.objects.filter(logement__lot_id=convention.lot.id).exclude(
        uuid__in=obj_uuids
    ).delete()
    for form_stationnement in formset:
        if form_stationnement.cleaned_data["uuid"]:
            stationnement = TypeStationnement.objects.get(
                uuid=form_stationnement.cleaned_data["uuid"]
            )
            stationnement.typologie = form_stationnement.cleaned_data["typologie"]
            stationnement.nb_stationnements = form_stationnement.cleaned_data[
                "nb_stationnements"
            ]
            stationnement.loyer = form_stationnement.cleaned_data["loyer"]
        else:
            stationnement = TypeStationnement.objects.create(
                lot=convention.lot,
                bailleur=convention.bailleur,
                typologie=form_stationnement.cleaned_data["typologie"],
                nb_stationnements=form_stationnement.cleaned_data["nb_stationnements"],
                loyer=form_stationnement.cleaned_data["loyer"],
            )
        stationnement.save()
