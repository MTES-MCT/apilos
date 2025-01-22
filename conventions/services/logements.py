from conventions.forms import (
    FoyerResidenceLogementFormSet,
    LogementCorrigeeFormSet,
    LogementCorrigeeSansLoyerFormSet,
    LogementFormSet,
    LogementSansLoyerFormSet,
    LotFoyerResidenceLgtsDetailsForm,
    LotLgtsOptionForm,
    UploadForm,
)
from conventions.services import upload_objects, utils
from conventions.services.conventions import ConventionService
from programmes.models import Logement, LogementCorrigee, LogementCorrigeeSansLoyer
from programmes.models.models import LogementSansLoyer


class ConventionLogementsService(ConventionService):
    form: LotLgtsOptionForm
    formset: LogementFormSet
    formset_sans_loyer: LogementSansLoyerFormSet
    formset_corrigee: LogementCorrigeeFormSet
    formset_corrigee_sans_loyer: LogementCorrigeeSansLoyerFormSet
    upform: UploadForm = UploadForm()

    def initialize_formsets(self):
        initial = []
        initial_sans_loyer = []
        initial_corrigee = []
        initial_corrigee_sans_loyer = []
        logements = self.convention.lot.logements.order_by("import_order")
        for logement in logements:
            common_params = {
                "uuid": logement.uuid,
                "designation": logement.designation,
                "typologie": logement.typologie,
                "surface_habitable": logement.surface_habitable,
            }
            surface_annexes_params = {
                "surface_annexes": logement.surface_annexes,
                "surface_annexes_retenue": logement.surface_annexes_retenue,
            }
            loyer_params = {
                "loyer_par_metre_carre": logement.loyer_par_metre_carre,
                "coeficient": logement.coeficient,
                "loyer": logement.loyer,
            }
            surface_utile_params = {
                "surface_utile": logement.surface_utile,
            }
            surface_corrigee_params = {
                "surface_corrigee": logement.surface_corrigee,
            }
            if logement.loyer:
                if logement.surface_corrigee:
                    initial_corrigee.append(
                        {
                            **common_params,
                            **surface_corrigee_params,
                            **loyer_params,
                        }
                    )
                else:
                    initial.append(
                        {
                            **common_params,
                            **surface_annexes_params,
                            **surface_utile_params,
                            **loyer_params,
                        }
                    )
            else:
                if logement.surface_corrigee:
                    initial_corrigee_sans_loyer.append(
                        {
                            **common_params,
                            **surface_corrigee_params,
                        }
                    )
                else:
                    initial_sans_loyer.append(
                        {
                            **common_params,
                            **surface_annexes_params,
                            **surface_utile_params,
                        }
                    )

        self.formset = LogementFormSet(initial=initial, prefix="avec_loyer")
        self.formset_sans_loyer = LogementSansLoyerFormSet(
            initial=initial_sans_loyer, prefix="sans_loyer"
        )
        self.formset_corrigee = LogementCorrigeeFormSet(
            initial=initial_corrigee, prefix="corrigee_avec_loyer"
        )
        self.formset_corrigee_sans_loyer = LogementCorrigeeSansLoyerFormSet(
            initial=initial_corrigee_sans_loyer, prefix="corrigee_sans_loyer"
        )

    def get(self):
        self.initialize_formsets()
        self.form = LotLgtsOptionForm(
            initial={
                "uuid": self.convention.lot.uuid,
                "lgts_mixite_sociale_negocies": self.convention.lot.lgts_mixite_sociale_negocies,
                "loyer_derogatoire": self.convention.lot.loyer_derogatoire,
                "surface_locaux_collectifs_residentiels": (
                    self.convention.lot.surface_locaux_collectifs_residentiels
                ),
                "loyer_associations_foncieres": self.convention.lot.loyer_associations_foncieres,
                "nb_logements": self.convention.lot.nb_logements,
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        if self.request.POST.get("Upload", False):
            self.form = LotLgtsOptionForm(self.request.POST)
            if self.request.POST["Upload"] == "file_sans_loyer":
                self._upload_logements_sans_loyer()
            elif self.request.POST["Upload"] == "file_corrigee":
                self._upload_logements_corrigee()
            elif self.request.POST["Upload"] == "file_corrigee_sans_loyer":
                self._upload_logements_corrigee_sans_loyer()
            else:
                self._upload_logements()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._logements_atomic_update()

    def _upload_logements_corrigee(self):
        self.formset_corrigee = LogementCorrigeeFormSet(
            self.request.POST, prefix="corrigee_avec_loyer"
        )
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                LogementCorrigee,
                self.convention,
                "logements_corrigee.xlsx",
                import_order=True,
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                lgts_by_designation = {}
                for lgt in Logement.objects.filter(lot_id=self.convention.lot.id):
                    lgts_by_designation[lgt.designation] = lgt.uuid
                for obj in result["objects"]:
                    if (
                        "designation" in obj
                        and obj["designation"] in lgts_by_designation
                    ):
                        obj["uuid"] = lgts_by_designation[obj["designation"]]
                self.initialize_formsets()
                self.formset_corrigee = LogementCorrigeeFormSet(
                    initial=result["objects"], prefix="corrigee_avec_loyer"
                )
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _upload_logements_corrigee_sans_loyer(self):
        self.formset_corrigee_sans_loyer = LogementCorrigeeSansLoyerFormSet(
            self.request.POST, prefix="corrigee_sans_loyer"
        )
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                LogementCorrigeeSansLoyer,
                self.convention,
                "logements_corrigee_sans_loyer.xlsx",
                import_order=True,
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                lgts_by_designation = {}
                for lgt in Logement.objects.filter(lot_id=self.convention.lot.id):
                    lgts_by_designation[lgt.designation] = lgt.uuid
                for obj in result["objects"]:
                    if (
                        "designation" in obj
                        and obj["designation"] in lgts_by_designation
                    ):
                        obj["uuid"] = lgts_by_designation[obj["designation"]]
                self.initialize_formsets()
                self.formset_corrigee_sans_loyer = LogementCorrigeeSansLoyerFormSet(
                    initial=result["objects"], prefix="corrigee_sans_loyer"
                )
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _upload_logements_sans_loyer(self):
        self.formset_sans_loyer = LogementSansLoyerFormSet(
            self.request.POST, prefix="sans_loyer"
        )
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                LogementSansLoyer,
                self.convention,
                "logements_sans_loyer.xlsx",
                import_order=True,
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                lgts_by_designation = {}
                for lgt in Logement.objects.filter(lot_id=self.convention.lot.id):
                    lgts_by_designation[lgt.designation] = lgt.uuid
                for obj in result["objects"]:
                    if (
                        "designation" in obj
                        and obj["designation"] in lgts_by_designation
                    ):
                        obj["uuid"] = lgts_by_designation[obj["designation"]]
                self.initialize_formsets()
                self.formset_sans_loyer = LogementSansLoyerFormSet(
                    initial=result["objects"], prefix="sans_loyer"
                )
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    # TODO refacto ici
    def _upload_logements(self):
        self.formset = LogementFormSet(self.request.POST, prefix="avec_loyer")
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                Logement,
                self.convention,
                "logements.xlsx",
                import_order=True,
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                lgts_by_designation = {}
                for lgt in Logement.objects.filter(lot_id=self.convention.lot.id):
                    lgts_by_designation[lgt.designation] = lgt.uuid
                for obj in result["objects"]:
                    if (
                        "designation" in obj
                        and obj["designation"] in lgts_by_designation
                    ):
                        obj["uuid"] = lgts_by_designation[obj["designation"]]
                self.initialize_formsets()
                self.formset = LogementFormSet(
                    initial=result["objects"], prefix="avec_loyer"
                )
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _get_form_value(self, form_logement, field: str):
        if form_logement["uuid"].value():
            logement = Logement.objects.get(uuid=form_logement["uuid"].value())
            if field == "uuid":
                return logement.uuid
            return utils.get_form_value(form_logement, logement, field)
        else:
            if field == "uuid":
                return None
            return form_logement[field].value()

    def _add_logement_to_initformset(
        self, form_logement, idx, initformset, nb_logement, prefix
    ):
        initformset = {
            **initformset,
            f"{prefix}-{idx}-designation": self._get_form_value(
                form_logement, "designation"
            ),
            f"{prefix}-{idx}-typologie": self._get_form_value(
                form_logement, "typologie"
            ),
            f"{prefix}-{idx}-surface_habitable": self._get_form_value(
                form_logement, "surface_habitable"
            ),
            f"{prefix}-{idx}-import_order": self._get_form_value(
                form_logement, "import_order"
            ),
        }
        if form_logement["uuid"].value():
            logement = Logement.objects.get(uuid=form_logement["uuid"].value())
            initformset = {
                **initformset,
                f"{prefix}-{idx}-uuid": logement.uuid,
            }
        if "sans_loyer" not in prefix:
            initformset = {
                **initformset,
                f"{prefix}-{idx}-loyer_par_metre_carre": self._get_form_value(
                    form_logement, "loyer_par_metre_carre"
                ),
                f"{prefix}-{idx}-coeficient": self._get_form_value(
                    form_logement, "coeficient"
                ),
                f"{prefix}-{idx}-loyer": self._get_form_value(form_logement, "loyer"),
            }
        if "corrigee" in prefix:
            initformset = {
                **initformset,
                f"{prefix}-{idx}-surface_corrigee": self._get_form_value(
                    form_logement, "surface_corrigee"
                ),
            }
        else:
            initformset = {
                **initformset,
                f"{prefix}-{idx}-surface_annexes": self._get_form_value(
                    form_logement, "surface_annexes"
                ),
                f"{prefix}-{idx}-surface_annexes_retenue": self._get_form_value(
                    form_logement, "surface_annexes_retenue"
                ),
                f"{prefix}-{idx}-surface_utile": self._get_form_value(
                    form_logement, "surface_utile"
                ),
            }
        nb_logement = nb_logement + 1
        return initformset, nb_logement

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
                        "loyer_associations_foncieres",
                        "nb_logements",
                    ],
                    [
                        "formset_sans_loyer_disabled",
                        "formset_disabled",
                        "formset_corrigee_disabled",
                        "formset_corrigee_sans_loyer_disabled",
                    ],
                ),
            }
        )
        form_is_valid = self.form.is_valid()
        # TODO refacto
        self.formset = LogementFormSet(self.request.POST, prefix="avec_loyer")
        self.formset_sans_loyer = LogementSansLoyerFormSet(
            self.request.POST, prefix="sans_loyer"
        )
        self.formset_corrigee = LogementCorrigeeFormSet(
            self.request.POST, prefix="corrigee_avec_loyer"
        )
        self.formset_corrigee_sans_loyer = LogementCorrigeeSansLoyerFormSet(
            self.request.POST, prefix="corrigee_sans_loyer"
        )
        initformset = {}
        initformset_sans_loyer = {}
        initformset_corrigee = {}
        initformset_corrigee_sans_loyer = {}
        nb_logements = 0
        nb_logements_sans_loyer = 0
        nb_logements_corrigee = 0
        nb_logements_corrigee_sans_loyer = 0

        for idx, form_logement in enumerate(self.formset):
            result = self._add_logement_to_initformset(
                form_logement, idx, initformset, nb_logements, prefix="avec_loyer"
            )
            initformset = result[0]
            nb_logements = result[1]

        for idx, form_logement in enumerate(self.formset_sans_loyer):
            result = self._add_logement_to_initformset(
                form_logement,
                idx,
                initformset_sans_loyer,
                nb_logements_sans_loyer,
                prefix="sans_loyer",
            )
            initformset_sans_loyer = result[0]
            nb_logements_sans_loyer = result[1]

        for idx, form_logement in enumerate(self.formset_corrigee):
            result = self._add_logement_to_initformset(
                form_logement,
                idx,
                initformset_corrigee,
                nb_logements_corrigee,
                prefix="corrigee_avec_loyer",
            )
            initformset_corrigee = result[0]
            nb_logements_corrigee = result[1]

        for idx, form_logement in enumerate(self.formset_corrigee_sans_loyer):
            result = self._add_logement_to_initformset(
                form_logement,
                idx,
                initformset_corrigee_sans_loyer,
                nb_logements_corrigee_sans_loyer,
                prefix="corrigee_sans_loyer",
            )
            initformset_corrigee_sans_loyer = result[0]
            nb_logements_corrigee_sans_loyer = result[1]

        initformset = {
            **initformset,
            "avec_loyer-TOTAL_FORMS": nb_logements,
            "avec_loyer-INITIAL_FORMS": nb_logements,
        }
        initformset_sans_loyer = {
            **initformset_sans_loyer,
            "sans_loyer-TOTAL_FORMS": nb_logements_sans_loyer,
            "sans_loyer-INITIAL_FORMS": nb_logements_sans_loyer,
        }
        initformset_corrigee = {
            **initformset_corrigee,
            "corrigee_avec_loyer-TOTAL_FORMS": nb_logements_corrigee,
            "corrigee_avec_loyer-INITIAL_FORMS": nb_logements_corrigee,
        }
        initformset_corrigee_sans_loyer = {
            **initformset_corrigee_sans_loyer,
            "corrigee_sans_loyer-TOTAL_FORMS": nb_logements_corrigee_sans_loyer,
            "corrigee_sans_loyer-INITIAL_FORMS": nb_logements_corrigee_sans_loyer,
        }
        total_nb_logements = (
            nb_logements
            + nb_logements_sans_loyer
            + nb_logements_corrigee
            + nb_logements_corrigee_sans_loyer
        )
        self.formset = LogementFormSet(initformset, prefix="avec_loyer")
        self.formset.programme_id = self.convention.programme_id
        self.formset.lot_id = self.convention.lot.id
        self.formset.nb_logements = int(self.request.POST.get("nb_logements") or 0)
        self.formset.ignore_optional_errors = self.request.POST.get(
            "ignore_optional_errors", False
        )
        self.formset.total_nb_logements = total_nb_logements
        self.formset_sans_loyer = LogementSansLoyerFormSet(
            initformset_sans_loyer, prefix="sans_loyer"
        )
        self.formset_sans_loyer.programme_id = self.convention.programme_id
        self.formset_sans_loyer.lot_id = self.convention.lot.id
        self.formset_sans_loyer.nb_logements = int(
            self.request.POST.get("nb_logements") or 0
        )
        self.formset_sans_loyer.ignore_optional_errors = self.request.POST.get(
            "ignore_optional_errors", False
        )
        self.formset_sans_loyer.total_nb_logements = total_nb_logements
        self.formset_corrigee = LogementCorrigeeFormSet(
            initformset_corrigee, prefix="corrigee_avec_loyer"
        )
        self.formset_corrigee.programme_id = self.convention.programme_id
        self.formset_corrigee.lot_id = self.convention.lot.id
        self.formset_corrigee.nb_logements = int(
            self.request.POST.get("nb_logements") or 0
        )
        self.formset_corrigee.ignore_optional_errors = self.request.POST.get(
            "ignore_optional_errors", False
        )
        self.formset_corrigee.total_nb_logements = total_nb_logements
        self.formset_corrigee_sans_loyer = LogementCorrigeeSansLoyerFormSet(
            initformset_corrigee_sans_loyer, prefix="corrigee_sans_loyer"
        )
        self.formset_corrigee_sans_loyer.programme_id = self.convention.programme_id
        self.formset_corrigee_sans_loyer.lot_id = self.convention.lot.id
        self.formset_corrigee_sans_loyer.nb_logements = int(
            self.request.POST.get("nb_logements") or 0
        )
        self.formset_corrigee_sans_loyer.ignore_optional_errors = self.request.POST.get(
            "ignore_optional_errors", False
        )
        self.formset_corrigee_sans_loyer.total_nb_logements = total_nb_logements

        formset_is_valid = self.formset.is_valid()
        formset_sans_loyer_is_valid = self.formset_sans_loyer.is_valid()
        formset_corrigee_is_valid = self.formset_corrigee.is_valid()
        formset_corrigee_sans_loyer_is_valid = (
            self.formset_corrigee_sans_loyer.is_valid()
        )

        if (
            form_is_valid
            and formset_is_valid
            and formset_sans_loyer_is_valid
            and formset_corrigee_is_valid
            and formset_corrigee_sans_loyer_is_valid
        ):
            self._save_logements()
            self._save_logements_sans_loyer()
            self._save_logements_corrigee()
            self._save_logements_corrigee_sans_loyer()
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
        lot.loyer_associations_foncieres = self.form.cleaned_data[
            "loyer_associations_foncieres"
        ]
        lot.save()

    def _save_logements_sans_loyer(self):
        lgt_uuids1 = list(
            map(lambda x: x.cleaned_data["uuid"], self.formset_sans_loyer)
        )
        lgt_uuids = list(filter(None, lgt_uuids1))

        if self.form.cleaned_data["formset_sans_loyer_disabled"]:
            # Clear all logements sans loyer
            self.convention.lot.logements.filter(
                surface_corrigee__isnull=True, loyer__isnull=True
            ).delete()
            return
        else:
            self.convention.lot.logements.exclude(uuid__in=lgt_uuids).filter(
                surface_corrigee__isnull=True, loyer__isnull=True
            ).delete()
        for form_logement in self.formset_sans_loyer:
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
                logement.import_order = form_logement.cleaned_data["import_order"]
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
                    import_order=form_logement.cleaned_data["import_order"],
                )
            logement.save()

    def _save_logements(self):

        lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        lgt_uuids = list(filter(None, lgt_uuids1))
        if self.form.cleaned_data["formset_disabled"]:
            # Clear all logements avec loyer
            self.convention.lot.logements.filter(
                surface_corrigee__isnull=True, loyer__isnull=False
            ).delete()
            return
        else:
            self.convention.lot.logements.exclude(uuid__in=lgt_uuids).filter(
                surface_corrigee__isnull=True, loyer__isnull=False
            ).delete()
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
                logement.import_order = form_logement.cleaned_data["import_order"]
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
                    import_order=form_logement.cleaned_data["import_order"],
                )
            logement.save()

    def _save_logements_corrigee(self):
        lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset_corrigee))
        lgt_uuids = list(filter(None, lgt_uuids1))

        if self.form.cleaned_data["formset_corrigee_disabled"]:
            # Clear all logements with surface corrigée and loyer
            self.convention.lot.logements.filter(
                surface_corrigee__isnull=False, loyer__isnull=False
            ).delete()
            return
        else:
            self.convention.lot.logements.exclude(uuid__in=lgt_uuids).filter(
                surface_corrigee__isnull=False, loyer__isnull=False
            ).delete()
        for form_logement in self.formset_corrigee:
            if form_logement.cleaned_data["uuid"]:
                logement = Logement.objects.get(uuid=form_logement.cleaned_data["uuid"])
                logement.designation = form_logement.cleaned_data["designation"]
                logement.typologie = form_logement.cleaned_data["typologie"]
                logement.surface_habitable = form_logement.cleaned_data[
                    "surface_habitable"
                ]
                logement.surface_corrigee = form_logement.cleaned_data[
                    "surface_corrigee"
                ]
                logement.loyer_par_metre_carre = form_logement.cleaned_data[
                    "loyer_par_metre_carre"
                ]
                logement.coeficient = form_logement.cleaned_data["coeficient"]
                logement.loyer = form_logement.cleaned_data["loyer"]
                logement.import_order = form_logement.cleaned_data["import_order"]

            else:
                logement = Logement.objects.create(
                    lot=self.convention.lot,
                    designation=form_logement.cleaned_data["designation"],
                    typologie=form_logement.cleaned_data["typologie"],
                    surface_habitable=form_logement.cleaned_data["surface_habitable"],
                    surface_corrigee=form_logement.cleaned_data["surface_corrigee"],
                    loyer_par_metre_carre=form_logement.cleaned_data[
                        "loyer_par_metre_carre"
                    ],
                    coeficient=form_logement.cleaned_data["coeficient"],
                    loyer=form_logement.cleaned_data["loyer"],
                    import_order=form_logement.cleaned_data["import_order"],
                )
            logement.save()

    def _save_logements_corrigee_sans_loyer(self):
        lgt_uuids1 = list(
            map(lambda x: x.cleaned_data["uuid"], self.formset_corrigee_sans_loyer)
        )
        lgt_uuids = list(filter(None, lgt_uuids1))

        if self.form.cleaned_data["formset_corrigee_sans_loyer_disabled"]:
            # Clear all logements with surface corrigée and loyer
            self.convention.lot.logements.filter(
                surface_corrigee__isnull=False, loyer__isnull=True
            ).delete()
            return
        else:
            self.convention.lot.logements.exclude(uuid__in=lgt_uuids).filter(
                surface_corrigee__isnull=False, loyer__isnull=True
            ).delete()
        for form_logement in self.formset_corrigee_sans_loyer:
            if form_logement.cleaned_data["uuid"]:
                logement = Logement.objects.get(uuid=form_logement.cleaned_data["uuid"])
                logement.designation = form_logement.cleaned_data["designation"]
                logement.typologie = form_logement.cleaned_data["typologie"]
                logement.surface_habitable = form_logement.cleaned_data[
                    "surface_habitable"
                ]
                logement.surface_corrigee = form_logement.cleaned_data[
                    "surface_corrigee"
                ]
                logement.import_order = form_logement.cleaned_data["import_order"]
            else:
                logement = Logement.objects.create(
                    lot=self.convention.lot,
                    designation=form_logement.cleaned_data["designation"],
                    typologie=form_logement.cleaned_data["typologie"],
                    surface_habitable=form_logement.cleaned_data["surface_habitable"],
                    surface_corrigee=form_logement.cleaned_data["surface_corrigee"],
                    import_order=form_logement.cleaned_data["import_order"],
                )
            logement.save()


class ConventionFoyerResidenceLogementsService(ConventionService):
    form: LotFoyerResidenceLgtsDetailsForm
    formset: FoyerResidenceLogementFormSet
    upform: UploadForm = UploadForm()

    def get(self):
        initial = []
        logements = self.convention.lot.logements.order_by("import_order")
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
                import_order=True,
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                lgts_by_designation = {}
                for lgt in Logement.objects.filter(lot_id=self.convention.lot.id):
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
                    f"form-{idx}-import_order": utils.get_form_value(
                        form_logement, logement, "import_order"
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
                    f"form-{idx}-import_order": form_logement["import_order"].value(),
                }
        self.formset = FoyerResidenceLogementFormSet(initformset)
        self.formset.lot_id = self.convention.lot.id
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
        lot_convention = self.convention.lot
        lot_convention.surface_habitable_totale = self.form.cleaned_data[
            "surface_habitable_totale"
        ]
        lot_convention.nb_logements = self.form.cleaned_data["nb_logements"]
        lot_convention.save()

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
                logement.import_order = form_logement.cleaned_data["import_order"]
            else:
                logement = Logement.objects.create(
                    lot=self.convention.lot,
                    designation=form_logement.cleaned_data["designation"],
                    typologie=form_logement.cleaned_data["typologie"],
                    surface_habitable=form_logement.cleaned_data["surface_habitable"],
                    loyer=form_logement.cleaned_data["loyer"],
                    import_order=form_logement.cleaned_data["import_order"],
                )
            logement.save()
