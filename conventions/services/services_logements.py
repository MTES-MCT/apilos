from programmes.models import (
    Logement,
    Annexe,
    TypeStationnement,
)
from programmes.forms import (
    LogementFormSet,
    TypeStationnementFormSet,
    AnnexeFormSet,
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
                lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], formset))
                lgt_uuids = list(filter(None, lgt_uuids1))
                convention.lot.logement_set.exclude(uuid__in=lgt_uuids).delete()
                for form_logement in formset:
                    if form_logement.cleaned_data["uuid"]:
                        logement = Logement.objects.get(
                            uuid=form_logement.cleaned_data["uuid"]
                        )
                        logement.designation = form_logement.cleaned_data["designation"]
                        logement.typologie = form_logement.cleaned_data["typologie"]
                        logement.surface_habitable = form_logement.cleaned_data[
                            "surface_habitable"
                        ]
                        logement.surface_annexes = form_logement.cleaned_data[
                            "surface_annexes"
                        ]
                        logement.surface_annexes_retenue = form_logement.cleaned_data[
                            "surface_annexes_retenue"
                        ]
                        logement.surface_utile = form_logement.cleaned_data[
                            "surface_utile"
                        ]
                        logement.loyer_par_metre_carre = form_logement.cleaned_data[
                            "loyer_par_metre_carre"
                        ]
                        logement.coeficient = form_logement.cleaned_data["coeficient"]
                        logement.loyer = form_logement.cleaned_data["loyer"]
                        logement.save()
                    else:
                        logement = Logement.objects.create(
                            lot=convention.lot,
                            bailleur=convention.bailleur,
                            designation=form_logement.cleaned_data["designation"],
                            typologie=form_logement.cleaned_data["typologie"],
                            surface_habitable=form_logement.cleaned_data[
                                "surface_habitable"
                            ],
                            surface_annexes=form_logement.cleaned_data[
                                "surface_annexes"
                            ],
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
                # All is OK -> Next:
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "formset": formset,
                }
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
        # When the user cliked on "Téléverser" button
        formset = AnnexeFormSet(request.POST)
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
            # to do : manage this one in the model
            formset.is_valid()
            for form_annexe in formset:
                try:
                    logement = convention.lot.logement_set.get(
                        designation=form_annexe.cleaned_data["logement_designation"],
                        lot=convention.lot,
                    )
                except Logement.DoesNotExist:
                    form_annexe.add_error(
                        "logement_designation", "Ce logement n'existe pas dans ce lot"
                    )
            if formset.is_valid():
                Annexe.objects.filter(logement__lot_id=convention.lot.id).delete()
                for form_annexe in formset:
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
                        loyer_par_metre_carre=form_annexe.cleaned_data[
                            "loyer_par_metre_carre"
                        ],
                        loyer=form_annexe.cleaned_data["loyer"],
                    )
                    annexe.save()
                # All is OK -> Next:
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "formset": formset,
                }
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
    return {
        **utils.base_convention_response_error(request, convention),
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def stationnements_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__typestationnement_set")
        .get(uuid=convention_uuid)
    )
    import_warnings = None
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
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
                convention.lot.typestationnement_set.all().delete()
                for form_stationnement in formset:
                    stationnement = TypeStationnement.objects.create(
                        lot=convention.lot,
                        bailleur=convention.bailleur,
                        typologie=form_stationnement.cleaned_data["typologie"],
                        nb_stationnements=form_stationnement.cleaned_data[
                            "nb_stationnements"
                        ],
                        loyer=form_stationnement.cleaned_data["loyer"],
                    )
                    stationnement.save()
                # All is OK -> Next:
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "formset": formset,
                }
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
