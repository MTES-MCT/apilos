from conventions.forms import AnnexeFormSet, LotAnnexeForm, UploadForm
from conventions.services import upload_objects, utils
from conventions.services.conventions import ConventionService
from programmes.models import Annexe, Logement


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
