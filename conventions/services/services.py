import datetime

from programmes.models import (
    Lot,
    Logement,
    Annexe,
    TypeStationnement,
    LogementEDD,
    ReferenceCadastrale,
)
from programmes.forms import (
    ProgrammeSelectionForm,
    ProgrammeForm,
    ProgrammeCadastralForm,
    ProgrammeEDDForm,
    LogementFormSet,
    TypeStationnementFormSet,
    AnnexeFormSet,
    LogementEDDFormSet,
    ReferenceCadastraleFormSet,
)
from bailleurs.forms import BailleurForm
from conventions.models import Convention, ConventionStatut, Pret
from conventions.forms import (
    ConventionCommentForm,
    ConventionFinancementForm,
    PretFormSet,
    UploadForm,
)
from . import utils
from . import convention_generator
from . import upload_objects


def conventions_index(request, infilter):
    infilter.update(request.user.convention_filter())
    conventions = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .filter(**infilter)
    )
    return conventions


def conventions_selection(request, infilter):
    infilter.update(request.user.programme_filter())
    return (
        Lot.objects.prefetch_related("programme")
        .prefetch_related("convention_set")
        .filter(**infilter)
        .order_by("programme__nom", "financement")
    )


def select_programme_create(request):
    if request.method == "POST":
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            lot = Lot.objects.get(uuid=form.cleaned_data["lot_uuid"])
            convention = Convention.objects.create(
                lot=lot,
                programme_id=lot.programme_id,
                bailleur_id=lot.bailleur_id,
                financement=lot.financement,
            )
            convention.save()
            # All is OK -> Next:
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
                "form": form,
            }  # HttpResponseRedirect(reverse('conventions:bailleur', args=[convention.uuid]) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm()

    programmes = conventions_selection(request, {})
    return {
        "success": utils.ReturnStatus.ERROR,
        "programmes": programmes,
        "form": form,
    }  # render(request, "conventions/selection.html", {'form': form, 'programmes': programmes})


def select_programme_update(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == "POST":
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
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
                "form": form,
            }

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm(
            initial={
                "lot_uuid": str(convention.lot.uuid),
            }
        )

    programmes = conventions_selection(request, {})
    return {
        "success": utils.ReturnStatus.ERROR,
        "programmes": programmes,
        "convention_uuid": convention_uuid,
        "form": form,
    }


def bailleur_update(request, convention_uuid):
    convention = Convention.objects.prefetch_related("bailleur").get(
        uuid=convention_uuid
    )
    bailleur = convention.bailleur

    if request.method == "POST":
        #        if request.POST['convention_uuid'] is None:
        form = BailleurForm(request.POST)
        if form.is_valid():
            bailleur.nom = form.cleaned_data["nom"]
            bailleur.siret = form.cleaned_data["siret"]
            bailleur.capital_social = form.cleaned_data["capital_social"]
            bailleur.adresse = form.cleaned_data["adresse"]
            bailleur.code_postal = form.cleaned_data["code_postal"]
            bailleur.ville = form.cleaned_data["ville"]
            bailleur.dg_nom = form.cleaned_data["dg_nom"]
            bailleur.dg_fonction = form.cleaned_data["dg_fonction"]
            bailleur.dg_date_deliberation = form.cleaned_data["dg_date_deliberation"]
            bailleur.save()
            # All is OK -> Next:
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
                "form": form,
            }

    # If this is a GET (or any other method) create the default form.
    else:
        form = BailleurForm(
            initial={
                "nom": bailleur.nom,
                "siret": bailleur.siret,
                "capital_social": bailleur.capital_social,
                "adresse": bailleur.adresse,
                "code_postal": bailleur.code_postal,
                "ville": bailleur.ville,
                "dg_nom": bailleur.dg_nom,
                "dg_fonction": bailleur.dg_fonction,
                "dg_date_deliberation": utils.format_date_for_form(
                    bailleur.dg_date_deliberation
                ),
            }
        )

    return {"success": utils.ReturnStatus.ERROR, "convention": convention, "form": form}


def programme_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .get(uuid=convention_uuid)
    )
    programme = convention.programme
    lot = convention.lot

    if request.method == "POST":
        #        if request.POST['convention_uuid'] is None:
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme.nom = form.cleaned_data["nom"]
            programme.adresse = form.cleaned_data["adresse"]
            programme.code_postal = form.cleaned_data["code_postal"]
            programme.ville = form.cleaned_data["ville"]
            programme.type_habitat = form.cleaned_data["type_habitat"]
            programme.type_operation = form.cleaned_data["type_operation"]
            programme.anru = form.cleaned_data["anru"]
            programme.autre_locaux_hors_convention = form.cleaned_data[
                "autre_locaux_hors_convention"
            ]
            programme.nb_locaux_commerciaux = form.cleaned_data["nb_locaux_commerciaux"]
            programme.nb_bureaux = form.cleaned_data["nb_bureaux"]
            programme.save()
            lot.nb_logements = form.cleaned_data["nb_logements"]
            lot.save()
            # All is OK -> Next:
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
                "form": form,
            }

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeForm(
            initial={
                "nom": programme.nom,
                "adresse": programme.adresse,
                "code_postal": programme.code_postal,
                "ville": programme.ville,
                "nb_logements": lot.nb_logements,
                "type_habitat": programme.type_habitat,
                "type_operation": programme.type_operation,
                "anru": programme.anru,
                "autre_locaux_hors_convention": programme.autre_locaux_hors_convention,
                "nb_locaux_commerciaux": programme.nb_locaux_commerciaux,
                "nb_bureaux": programme.nb_bureaux,
            }
        )

    return {"success": utils.ReturnStatus.ERROR, "convention": convention, "form": form}


def programme_cadastral_update(request, convention_uuid):
    # pylint: disable=R0915
    convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("programme__referencecadastrale_set")
        .get(uuid=convention_uuid)
    )
    programme = convention.programme

    import_warnings = None

    if request.method == "POST":
        # When the user cliked on "Téléverser" button
        formset = ReferenceCadastraleFormSet(request.POST)
        form = ProgrammeCadastralForm(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = upload_objects.handle_uploaded_file(
                    upform,
                    request.FILES["file"],
                    ReferenceCadastrale,
                    convention,
                    "cadastre.xlsx",
                )
                if result["success"] != utils.ReturnStatus.ERROR:
                    formset = ReferenceCadastraleFormSet(initial=result["objects"])
                    import_warnings = result["import_warnings"]
        # When the user cliked on "Enregistrer et Suivant"
        else:
            upform = UploadForm()
            form_is_valid = form.is_valid()
            formset_is_valid = formset.is_valid()
            if form_is_valid and formset_is_valid:
                programme.permis_construire = form.cleaned_data["permis_construire"]
                programme.date_acte_notarie = form.cleaned_data["date_acte_notarie"]
                programme.date_achevement_previsible = form.cleaned_data[
                    "date_achevement_previsible"
                ]
                programme.date_achat = form.cleaned_data["date_achat"]
                programme.date_achevement = form.cleaned_data["date_achevement"]
                programme.vendeur = form.cleaned_data["vendeur"]
                programme.acquereur = form.cleaned_data["acquereur"]
                programme.reference_notaire = form.cleaned_data["reference_notaire"]
                programme.reference_publication_acte = form.cleaned_data[
                    "reference_publication_acte"
                ]
                programme.acte_de_propriete = form.cleaned_data["acte_de_propriete"]
                programme.acte_notarial = form.cleaned_data["acte_notarial"]
                programme.save()

                programme.referencecadastrale_set.all().delete()
                for form_referencecadastrale in formset:
                    referencecadastrale = ReferenceCadastrale.objects.create(
                        programme=programme,
                        bailleur=convention.bailleur,
                        section=form_referencecadastrale.cleaned_data["section"],
                        numero=form_referencecadastrale.cleaned_data["numero"],
                        lieudit=form_referencecadastrale.cleaned_data["lieudit"],
                        surface=form_referencecadastrale.cleaned_data["surface"],
                    )
                    referencecadastrale.save()

                # All is OK -> Next:
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "form": form,
                    "formset": formset,
                }
    # When display the file for the first time
    else:
        initial = []
        referencecadastrales = programme.referencecadastrale_set.all()
        for referencecadastrale in referencecadastrales:
            initial.append(
                {
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
                "vendeur": programme.vendeur,
                "acquereur": programme.acquereur,
                "reference_notaire": programme.reference_notaire,
                "reference_publication_acte": programme.reference_publication_acte,
                "acte_de_propriete": programme.acte_de_propriete,
                "acte_notarial": programme.acte_notarial,
            }
        )
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
        "form": form,
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def programme_edd_update(request, convention_uuid):
    # pylint: disable=R0915
    convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("programme__logementedd_set")
        .get(uuid=convention_uuid)
    )
    programme = convention.programme

    import_warnings = None

    if request.method == "POST":
        # When the user cliked on "Téléverser" button
        formset = LogementEDDFormSet(request.POST)
        form = ProgrammeEDDForm(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = upload_objects.handle_uploaded_file(
                    upform,
                    request.FILES["file"],
                    LogementEDD,
                    convention,
                    "logements_edd.xlsx",
                )
                if result["success"] != utils.ReturnStatus.ERROR:
                    formset = LogementEDDFormSet(initial=result["objects"])
                    import_warnings = result["import_warnings"]
        # When the user cliked on "Enregistrer et Suivant"
        else:
            upform = UploadForm()
            form_is_valid = form.is_valid()
            formset_is_valid = formset.is_valid()
            if form_is_valid and formset_is_valid:
                programme.edd_volumetrique = form.cleaned_data["edd_volumetrique"]
                programme.save()

                programme.logementedd_set.all().delete()
                for form_logementedd in formset:
                    logementedd = LogementEDD.objects.create(
                        programme=programme,
                        bailleur=convention.bailleur,
                        financement=form_logementedd.cleaned_data["financement"],
                        designation=form_logementedd.cleaned_data["designation"],
                        typologie=form_logementedd.cleaned_data["typologie"],
                    )
                    logementedd.save()

                # All is OK -> Next:
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "form": form,
                    "formset": formset,
                }
    # When display the file for the first time
    else:
        initial = []
        logementedds = programme.logementedd_set.all()
        for logementedd in logementedds:
            initial.append(
                {
                    "financement": logementedd.financement,
                    "designation": logementedd.designation,
                    "typologie": logementedd.typologie,
                }
            )
        formset = LogementEDDFormSet(initial=initial)
        upform = UploadForm()
        form = ProgrammeEDDForm(
            initial={
                "edd_volumetrique": programme.edd_volumetrique,
            }
        )
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
        "form": form,
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def convention_financement(request, convention_uuid):
    convention = Convention.objects.prefetch_related("pret_set").get(
        uuid=convention_uuid
    )
    import_warnings = None

    if request.method == "POST":
        # When the user cliked on "Téléverser" button
        formset = PretFormSet(request.POST)
        form = ConventionFinancementForm(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = upload_objects.handle_uploaded_file(
                    upform, request.FILES["file"], Pret, convention, "prets.xlsx"
                )
                if result["success"] != utils.ReturnStatus.ERROR:
                    formset = PretFormSet(initial=result["objects"])
                    import_warnings = result["import_warnings"]
        # When the user cliked on "Enregistrer et Suivant"
        else:
            upform = UploadForm()
            form_is_valid = form.is_valid()
            formset_is_valid = formset.is_valid()
            if form_is_valid and formset_is_valid:
                convention.date_fin_conventionnement = form.cleaned_data[
                    "date_fin_conventionnement"
                ]
                convention.fond_propre = form.cleaned_data["fond_propre"]
                convention.save()
                convention.pret_set.all().delete()
                for form_pret in formset:
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

                # All is OK -> Next:
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "form": form,
                    "formset": formset,
                }
    # When display the file for the first time
    else:
        initial = []
        prets = convention.pret_set.all()
        for pret in prets:
            initial.append(
                {
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
                "date_fin_conventionnement": utils.format_date_for_form(
                    convention.date_fin_conventionnement
                ),
                "fond_propre": convention.fond_propre,
            }
        )
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
        "form": form,
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def logements_update(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("lot")
        .prefetch_related("lot__logement_set")
        .get(uuid=convention_uuid)
    )
    import_warnings = None

    if request.method == "POST":
        # When the user cliked on "Téléverser" button
        formset = LogementFormSet(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = upload_objects.handle_uploaded_file(
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
                print(type(lgt_uuids))
                print(lgt_uuids)
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
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
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
        # When the user cliked on "Téléverser" button
        formset = AnnexeFormSet(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = upload_objects.handle_uploaded_file(
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
        initial = []
        annexes = Annexe.objects.filter(logement__lot_id=convention.lot.id)
        for annexe in annexes:
            initial.append(
                {
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
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
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
        # When the user cliked on "Téléverser" button
        formset = TypeStationnementFormSet(request.POST)
        if request.POST.get("Upload", False):
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = upload_objects.handle_uploaded_file(
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
        initial = []
        stationnements = convention.lot.typestationnement_set.all()
        for stationnement in stationnements:
            initial.append(
                {
                    "typologie": stationnement.typologie,
                    "nb_stationnements": stationnement.nb_stationnements,
                    "loyer": stationnement.loyer,
                }
            )
        upform = UploadForm()
        formset = TypeStationnementFormSet(initial=initial)
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
        "formset": formset,
        "upform": upform,
        "import_warnings": import_warnings,
    }


def convention_comments(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == "POST":
        form = ConventionCommentForm(request.POST)
        if form.is_valid():
            convention.comments = form.cleaned_data["comments"]
            convention.save()
            # All is OK -> Next:
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
                "form": form,
            }

    else:
        form = ConventionCommentForm(
            initial={
                "comments": convention.comments,
            }
        )

    return {"success": utils.ReturnStatus.ERROR, "convention": convention, "form": form}


def convention_summary(request, convention_uuid):
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
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
        "bailleur": convention.bailleur,
        "lot": convention.lot,
        "programme": convention.programme,
        "logement_edds": convention.programme.logementedd_set.all(),
        "logements": convention.lot.logement_set.all(),
        "stationnements": convention.lot.typestationnement_set.all(),
        "reference_cadastrales": convention.programme.referencecadastrale_set.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
    }


def convention_save(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    submitted = utils.ReturnStatus.WARNING
    if request.method == "POST":
        if request.POST.get("SubmitConvention", False):
            convention.soumis_le = datetime.datetime.now()
            convention.statut = ConventionStatut.INSTRUCTION
            convention.save()
            submitted = utils.ReturnStatus.SUCCESS
        return {
            "success": submitted,
            "convention": convention,
        }
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
    }


def convention_validate(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    if request.method == "POST":
        if not convention.valide_le:
            convention.valide_le = datetime.datetime.now()
        convention.statut = ConventionStatut.VALIDE
        convention.save()
        submitted = utils.ReturnStatus.SUCCESS
        return {
            "success": submitted,
            "convention": convention,
        }
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
    }


def generate_convention(convention_uuid):
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
