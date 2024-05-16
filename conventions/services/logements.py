from conventions.forms import (
    FoyerResidenceLogementFormSet,
    LogementFormSet,
    LotFoyerResidenceLgtsDetailsForm,
    LotLgtsOptionForm,
    UploadForm,
)
from conventions.services import upload_objects, utils
from conventions.services.conventions import ConventionService
from programmes.models import Logement


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
                "surface_locaux_collectifs_residentiels": (
                    self.convention.lot.surface_locaux_collectifs_residentiels
                ),
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
                        "surface_locaux_collectifs_residentiels",
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
        self.formset.nb_logements = int(self.request.POST.get("nb_logements") or 0)
        self.formset.ignore_optional_errors = self.request.POST.get(
            "ignore_optional_errors", False
        )
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
        lot.nb_logements = self.form.cleaned_data["nb_logements"]
        lot.surface_locaux_collectifs_residentiels = (
            self.form.cleaned_data["surface_locaux_collectifs_residentiels"] or 0
        )
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
                "nb_logements": self.convention.lot.nb_logements,
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        if self.request.POST.get("Upload", False):
            self.form = LotFoyerResidenceLgtsDetailsForm(initial=self.request.POST)
            self._upload_foyer_residence_logements()
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
        self.formset.lot_id = self.convention.lot_id
        self.formset.nb_logements = int(self.request.POST.get("nb_logements") or 0)
        self.formset.ignore_optional_errors = self.request.POST.get(
            "ignore_optional_errors", False
        )
        formset_is_valid = self.formset.is_valid()

        self.form = LotFoyerResidenceLgtsDetailsForm(
            {
                "uuid": self.convention.lot.uuid,
                "surface_habitable_totale": self.request.POST.get(
                    "surface_habitable_totale",
                    self.convention.lot.surface_habitable_totale,
                ),
                "nb_logements": self.request.POST.get(
                    "nb_logements", self.convention.lot.nb_logements
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
        self.convention.lot.nb_logements = self.form.cleaned_data["nb_logements"]
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
