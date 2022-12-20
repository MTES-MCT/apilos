from typing import List

from django.http import HttpRequest

from conventions.forms import UploadForm
from conventions.models import Convention
from conventions.services.services_conventions import ConventionService
from programmes.forms import (
    AnnexeFormSet,
    FoyerResidenceLogementFormSet,
    LogementFormSet,
    LotAnnexeForm,
    LotFoyerResidenceLgtsDetailsForm,
    LotLgtsOptionForm,
    TypeStationnementFormSet,
)
from programmes.models import Annexe, Logement, TypeStationnement

from . import upload_objects, utils


class ConventionLogementsService(ConventionService):
    form: LotLgtsOptionForm
    formset: LogementFormSet
    upform: UploadForm = UploadForm()

    def get(self):
        initial = []
        logements = self.convention.lot.logements.all()
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
        self.formset = LogementFormSet(initial=initial)
        self.form = LotLgtsOptionForm(
            initial={
                "uuid": self.convention.lot.uuid,
                "lgts_mixite_sociale_negocies": self.convention.lot.lgts_mixite_sociale_negocies,
                "loyer_derogatoire": self.convention.lot.loyer_derogatoire,
                "nb_logements": self.convention.lot.nb_logements,
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        if self.request.POST.get("Upload", False):
            self.form = LotLgtsOptionForm(self.request.POST)
            self._upload_logements()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._logements_atomic_update()

    def _upload_logements(self):
        self.formset = LogementFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                Logement,
                self.convention,
                "logements.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                lgts_by_designation = {}
                for lgt in Logement.objects.filter(lot_id=self.convention.lot_id):
                    lgts_by_designation[lgt.designation] = lgt.uuid
                for obj in result["objects"]:
                    if (
                        "designation" in obj
                        and obj["designation"] in lgts_by_designation
                    ):
                        obj["uuid"] = lgts_by_designation[obj["designation"]]
                self.formset = LogementFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _logements_atomic_update(self):
        self.form = LotLgtsOptionForm(
            {
                "uuid": self.convention.lot.uuid,
                **utils.build_partial_form(
                    self.request,
                    self.convention.lot,
                    [
                        "lgts_mixite_sociale_negocies",
                        "loyer_derogatoire",
                        "nb_logements",
                    ],
                ),
            }
        )
        form_is_valid = self.form.is_valid()

        self.formset = LogementFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_logement in enumerate(self.formset):
            if form_logement["uuid"].value():
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
                    f"form-{idx}-loyer": utils.get_form_value(
                        form_logement, logement, "loyer"
                    ),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-designation": form_logement["designation"].value(),
                    f"form-{idx}-typologie": form_logement["typologie"].value(),
                    f"form-{idx}-surface_habitable": form_logement[
                        "surface_habitable"
                    ].value(),
                    f"form-{idx}-surface_annexes": form_logement[
                        "surface_annexes"
                    ].value(),
                    f"form-{idx}-surface_annexes_retenue": form_logement[
                        "surface_annexes_retenue"
                    ].value(),
                    f"form-{idx}-surface_utile": form_logement["surface_utile"].value(),
                    f"form-{idx}-loyer_par_metre_carre": form_logement[
                        "loyer_par_metre_carre"
                    ].value(),
                    f"form-{idx}-coeficient": form_logement["coeficient"].value(),
                    f"form-{idx}-loyer": form_logement["loyer"].value(),
                }
        self.formset = LogementFormSet(initformset)
        self.formset.programme_id = self.convention.programme_id
        self.formset.lot_id = self.convention.lot_id
        nb_logements = self.request.POST.get("nb_logements", None)
        self.formset.nb_logements = int(nb_logements) if nb_logements else None
        formset_is_valid = self.formset.is_valid()

        if form_is_valid and formset_is_valid:
            self._save_logements()
            self._save_lot_lgts_option()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_lot_lgts_option(self):
        lot = self.convention.lot
        lot.lgts_mixite_sociale_negocies = (
            self.form.cleaned_data["lgts_mixite_sociale_negocies"] or 0
        )
        lot.loyer_derogatoire = self.form.cleaned_data["loyer_derogatoire"]
        if "nb_logements" in self.form.cleaned_data:
            lot.nb_logements = self.form.cleaned_data["nb_logements"]
        lot.save()

    def _save_logements(self):
        lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        lgt_uuids = list(filter(None, lgt_uuids1))
        self.convention.lot.logements.exclude(uuid__in=lgt_uuids).delete()
        for form_logement in self.formset:
            if form_logement.cleaned_data["uuid"]:
                logement = Logement.objects.get(uuid=form_logement.cleaned_data["uuid"])
                logement.designation = form_logement.cleaned_data["designation"]
                logement.typologie = form_logement.cleaned_data["typologie"]
                logement.surface_habitable = form_logement.cleaned_data[
                    "surface_habitable"
                ]
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
                    lot=self.convention.lot,
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


class ConventionFoyerResidenceLogementsService(ConventionService):
    form: LotFoyerResidenceLgtsDetailsForm
    formset: FoyerResidenceLogementFormSet
    upform: UploadForm = UploadForm()

    def get(self):
        initial = []
        logements = self.convention.lot.logements.all()
        for logement in logements:
            initial.append(
                {
                    "uuid": logement.uuid,
                    "designation": logement.designation,
                    "typologie": logement.typologie,
                    "surface_habitable": logement.surface_habitable,
                    "loyer": logement.loyer,
                }
            )
        self.formset = FoyerResidenceLogementFormSet(initial=initial)
        self.form = LotFoyerResidenceLgtsDetailsForm(
            initial={
                "uuid": self.convention.lot.uuid,
                "surface_habitable_totale": self.convention.lot.surface_habitable_totale,
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        if self.request.POST.get("Upload", False):
            self.form = LotFoyerResidenceLgtsDetailsForm(self.request.POST)
            self._upload_foyer_residence_logements()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._foyer_residence_logements_atomic_update()

    def _upload_foyer_residence_logements(self):
        self.formset = FoyerResidenceLogementFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                Logement,
                self.convention,
                "foyer_residence_logements.xlsx",
                class_field_mapping="foyer_residence_import_mapping",
                class_field_needed_mapping="foyer_residence_needed_in_mapping",
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                lgts_by_designation = {}
                for lgt in Logement.objects.filter(lot_id=self.convention.lot_id):
                    lgts_by_designation[lgt.designation] = lgt.uuid
                for obj in result["objects"]:
                    if (
                        "designation" in obj
                        and obj["designation"] in lgts_by_designation
                    ):
                        obj["uuid"] = lgts_by_designation[obj["designation"]]
                self.formset = FoyerResidenceLogementFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _foyer_residence_logements_atomic_update(self):

        self.formset = FoyerResidenceLogementFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        surface_habitable_totale = 0
        for idx, form_logement in enumerate(self.formset):
            surface_habitable_totale += (
                float(form_logement["surface_habitable"].value())
                if form_logement["surface_habitable"].value()
                else 0
            )
            if form_logement["uuid"].value():
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
                    f"form-{idx}-loyer": utils.get_form_value(
                        form_logement, logement, "loyer"
                    ),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-designation": form_logement["designation"].value(),
                    f"form-{idx}-typologie": form_logement["typologie"].value(),
                    f"form-{idx}-surface_habitable": form_logement[
                        "surface_habitable"
                    ].value(),
                    f"form-{idx}-loyer": form_logement["loyer"].value(),
                }
        self.formset = FoyerResidenceLogementFormSet(initformset)
        formset_is_valid = self.formset.is_valid()

        self.form = LotFoyerResidenceLgtsDetailsForm(
            {
                "uuid": self.convention.lot.uuid,
                "surface_habitable_totale": self.request.POST.get(
                    "surface_habitable_totale",
                    getattr(self.convention.lot, "surface_habitable_totale"),
                ),
            }
        )

        self.form.floor_surface_habitable_totale = surface_habitable_totale
        form_is_valid = self.form.is_valid()

        if form_is_valid and formset_is_valid:
            self._save_foyer_residence_logements()
            self._save_lot_foyer_residence_lgts_details()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_lot_foyer_residence_lgts_details(self):
        self.convention.lot.surface_habitable_totale = self.form.cleaned_data[
            "surface_habitable_totale"
        ]
        self.convention.lot.save()

    def _save_foyer_residence_logements(self):
        lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        lgt_uuids = list(filter(None, lgt_uuids1))
        self.convention.lot.logements.exclude(uuid__in=lgt_uuids).delete()
        for form_logement in self.formset:
            if form_logement.cleaned_data["uuid"]:
                logement = Logement.objects.get(uuid=form_logement.cleaned_data["uuid"])
                logement.designation = form_logement.cleaned_data["designation"]
                logement.typologie = form_logement.cleaned_data["typologie"]
                logement.surface_habitable = form_logement.cleaned_data[
                    "surface_habitable"
                ]
                logement.loyer = form_logement.cleaned_data["loyer"]
            else:
                logement = Logement.objects.create(
                    lot=self.convention.lot,
                    designation=form_logement.cleaned_data["designation"],
                    typologie=form_logement.cleaned_data["typologie"],
                    surface_habitable=form_logement.cleaned_data["surface_habitable"],
                    loyer=form_logement.cleaned_data["loyer"],
                )
            logement.save()


class ConventionAnnexesService(ConventionService):
    form: LotAnnexeForm
    formset: AnnexeFormSet
    upform: UploadForm = UploadForm()

    def get(self):
        initial = []
        annexes = Annexe.objects.filter(logement__lot_id=self.convention.lot.id)
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
        self.formset = AnnexeFormSet(initial=initial)
        lot = self.convention.lot
        self.form = LotAnnexeForm(
            initial={
                "uuid": lot.uuid,
                "annexe_caves": lot.annexe_caves,
                "annexe_soussols": lot.annexe_soussols,
                "annexe_remises": lot.annexe_remises,
                "annexe_ateliers": lot.annexe_ateliers,
                "annexe_sechoirs": lot.annexe_sechoirs,
                "annexe_celliers": lot.annexe_celliers,
                "annexe_resserres": lot.annexe_resserres,
                "annexe_combles": lot.annexe_combles,
                "annexe_balcons": lot.annexe_balcons,
                "annexe_loggias": lot.annexe_loggias,
                "annexe_terrasses": lot.annexe_terrasses,
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        if self.request.POST.get("Upload", False):

            self.form = LotAnnexeForm(self.request.POST)
            self._upload_annexes()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._annexes_atomic_update()

    def _upload_annexes(self):
        self.formset = AnnexeFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                Annexe,
                self.convention,
                "annexes.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:

                annexes_by_designation = {}
                for annexe in Annexe.objects.prefetch_related("logement").filter(
                    logement__lot_id=self.convention.lot.id
                ):
                    annexes_by_designation[
                        f"{annexe.logement.designation}_{annexe.typologie}"
                    ] = annexe.uuid

                for obj in result["objects"]:
                    if (
                        "logement_designation" in obj
                        and "typologie" in obj
                        and f"{obj['logement_designation']}_{obj['typologie']}"
                        in annexes_by_designation
                    ):
                        obj["uuid"] = annexes_by_designation[
                            f"{obj['logement_designation']}_{obj['typologie']}"
                        ]

                self.formset = AnnexeFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _save_lot_annexes(self):
        lot = self.convention.lot
        lot.annexe_caves = self.form.cleaned_data["annexe_caves"]
        lot.annexe_soussols = self.form.cleaned_data["annexe_soussols"]
        lot.annexe_remises = self.form.cleaned_data["annexe_remises"]
        lot.annexe_ateliers = self.form.cleaned_data["annexe_ateliers"]
        lot.annexe_sechoirs = self.form.cleaned_data["annexe_sechoirs"]
        lot.annexe_celliers = self.form.cleaned_data["annexe_celliers"]
        lot.annexe_resserres = self.form.cleaned_data["annexe_resserres"]
        lot.annexe_combles = self.form.cleaned_data["annexe_combles"]
        lot.annexe_balcons = self.form.cleaned_data["annexe_balcons"]
        lot.annexe_loggias = self.form.cleaned_data["annexe_loggias"]
        lot.annexe_terrasses = self.form.cleaned_data["annexe_terrasses"]
        lot.save()

    def _annexes_atomic_update(self):
        self.form = LotAnnexeForm(
            {
                "uuid": self.convention.lot.uuid,
                **utils.build_partial_form(
                    self.request,
                    self.convention.lot,
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
        form_is_valid = self.form.is_valid()

        self.formset = AnnexeFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_annexe in enumerate(self.formset):
            if form_annexe["uuid"].value():
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
                    f"form-{idx}-loyer": utils.get_form_value(
                        form_annexe, annexe, "loyer"
                    ),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-typologie": form_annexe["typologie"].value(),
                    f"form-{idx}-logement_designation": form_annexe[
                        "logement_designation"
                    ].value(),
                    f"form-{idx}-logement_typologie": form_annexe[
                        "logement_typologie"
                    ].value(),
                    f"form-{idx}-surface_hors_surface_retenue": form_annexe[
                        "surface_hors_surface_retenue"
                    ].value(),
                    f"form-{idx}-loyer_par_metre_carre": form_annexe[
                        "loyer_par_metre_carre"
                    ].value(),
                    f"form-{idx}-loyer": form_annexe["loyer"].value(),
                }
        self.formset = AnnexeFormSet(initformset)
        self.formset.convention = self.convention
        formset_is_valid = self.formset.is_valid()

        if form_is_valid and formset_is_valid:
            self._save_lot_annexes()
            self._save_annexes()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_annexes(self):
        obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        obj_uuids = list(filter(None, obj_uuids1))
        Annexe.objects.filter(logement__lot_id=self.convention.lot.id).exclude(
            uuid__in=obj_uuids
        ).delete()
        for form_annexe in self.formset:
            if form_annexe.cleaned_data["uuid"]:
                annexe = Annexe.objects.get(uuid=form_annexe.cleaned_data["uuid"])
                logement = Logement.objects.get(
                    designation=form_annexe.cleaned_data["logement_designation"],
                    lot=self.convention.lot,
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
                    lot=self.convention.lot,
                )
                annexe = Annexe.objects.create(
                    logement=logement,
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


class ConventionTypeStationnementService(ConventionService):
    convention: Convention
    request: HttpRequest
    formset: TypeStationnementFormSet
    upform: UploadForm = UploadForm()
    editable_after_upload: bool
    redirect_recap: bool = False
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    import_warnings: None | List = None

    def get(self):
        self.editable_after_upload = bool(
            self.request.POST.get("editable_after_upload", False)
        )
        initial = []
        stationnements = self.convention.lot.type_stationnements.all()
        for stationnement in stationnements:
            initial.append(
                {
                    "uuid": stationnement.uuid,
                    "typologie": stationnement.typologie,
                    "nb_stationnements": stationnement.nb_stationnements,
                    "loyer": stationnement.loyer,
                }
            )
        self.formset = TypeStationnementFormSet(initial=initial)

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        # When the user cliked on "Téléverser" button
        if self.request.POST.get("Upload", False):
            self._upload_stationnements()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self.redirect_recap = bool(
                self.request.POST.get("redirect_to_recap", False)
            )
            self._stationnements_atomic_update()

    def _upload_stationnements(self):
        self.formset = TypeStationnementFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():

            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                TypeStationnement,
                self.convention,
                "stationnements.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                stationnement_by_designation = {}
                for stationnement in TypeStationnement.objects.filter(
                    lot_id=self.convention.lot_id
                ):
                    stationnement_by_designation[
                        f"{stationnement.nb_stationnements}_{stationnement.typologie}"
                    ] = stationnement.uuid

                for obj in result["objects"]:
                    if (
                        "nb_stationnements" in obj
                        and "typologie" in obj
                        and f"{obj['nb_stationnements']}_{obj['typologie']}"
                        in stationnement_by_designation
                    ):
                        obj["uuid"] = stationnement_by_designation[
                            f"{obj['nb_stationnements']}_{obj['typologie']}"
                        ]

                self.formset = TypeStationnementFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _stationnements_atomic_update(self):
        self.formset = TypeStationnementFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_stationnement in enumerate(self.formset):
            if form_stationnement["uuid"].value():
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
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-typologie": form_stationnement["typologie"].value(),
                    f"form-{idx}-nb_stationnements": form_stationnement[
                        "nb_stationnements"
                    ].value(),
                    f"form-{idx}-loyer": form_stationnement["loyer"].value(),
                }

        self.formset = TypeStationnementFormSet(initformset)
        if self.formset.is_valid():
            self._save_stationnements()
            self.return_status = utils.ReturnStatus.SUCCESS
        else:
            self.return_status = utils.ReturnStatus.ERROR

    def _save_stationnements(self):
        obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        obj_uuids = list(filter(None, obj_uuids1))
        TypeStationnement.objects.filter(lot_id=self.convention.lot.id).exclude(
            uuid__in=obj_uuids
        ).delete()
        for form_stationnement in self.formset:
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
                    lot=self.convention.lot,
                    typologie=form_stationnement.cleaned_data["typologie"],
                    nb_stationnements=form_stationnement.cleaned_data[
                        "nb_stationnements"
                    ],
                    loyer=form_stationnement.cleaned_data["loyer"],
                )
            stationnement.save()
