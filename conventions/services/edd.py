from django.http import HttpRequest

from conventions.forms import LogementEDDFormSet, ProgrammeEDDForm, UploadForm
from conventions.models import Convention
from conventions.services import upload_objects, utils
from conventions.services.conventions import ConventionService
from programmes.models import LogementEDD


class ConventionEDDService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ProgrammeEDDForm
    formset: LogementEDDFormSet
    upform: UploadForm = UploadForm()
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False
    editable_after_upload: bool = False

    def get(self):
        initial = []
        for logementedd in self.convention.programme.logementedds.all():
            initial.append(
                {
                    "uuid": logementedd.uuid,
                    "financement": logementedd.financement,
                    "designation": logementedd.designation,
                    "numero_lot": logementedd.numero_lot,
                }
            )
        self.formset = LogementEDDFormSet(initial=initial)
        self.form = ProgrammeEDDForm(
            initial={
                "uuid": self.convention.programme.uuid,
                "lot_uuid": self.convention.lots.first().uuid,
                **utils.get_text_and_files_from_field(
                    "edd_volumetrique",
                    self.convention.lots.first().edd_volumetrique,
                ),
                "mention_publication_edd_volumetrique": (
                    self.convention.programme.mention_publication_edd_volumetrique
                ),
                **utils.get_text_and_files_from_field(
                    "edd_classique",
                    self.convention.lots.first().edd_classique,
                ),
                "mention_publication_edd_classique": (
                    self.convention.programme.mention_publication_edd_classique
                ),
                **utils.get_text_and_files_from_field(
                    "edd_stationnements", self.convention.programme.edd_stationnements
                ),
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        # When the user cliked on "Déposer" button
        if self.request.POST.get("Upload", False):
            self.form = ProgrammeEDDForm(self.request.POST)
            self._upload_logements_edd()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._programme_edd_atomic_update()

    def _upload_logements_edd(self):
        self.formset = LogementEDDFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                LogementEDD,
                self.convention,
                "logements_edd.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                edd_lgts_by_designation = {}
                for edd_lgt in LogementEDD.objects.filter(
                    programme_id=self.convention.programme_id
                ):
                    edd_lgts_by_designation[edd_lgt.designation] = edd_lgt.uuid

                for obj in result["objects"]:
                    if (
                        "designation" in obj
                        and obj["designation"] in edd_lgts_by_designation
                    ):
                        obj["uuid"] = edd_lgts_by_designation[obj["designation"]]

                self.formset = LogementEDDFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _programme_edd_atomic_update(self):
        self.form = ProgrammeEDDForm(
            {
                "uuid": self.convention.programme.uuid,
                **utils.init_text_and_files_from_field(
                    self.request, self.convention.lots.first(), "edd_volumetrique"
                ),
                "mention_publication_edd_volumetrique": (
                    self.request.POST.get(
                        "mention_publication_edd_volumetrique",
                        self.convention.programme.mention_publication_edd_volumetrique,
                    )
                ),
                **utils.init_text_and_files_from_field(
                    self.request, self.convention.lots.first(), "edd_classique"
                ),
                "mention_publication_edd_classique": (
                    self.request.POST.get(
                        "mention_publication_edd_classique",
                        self.convention.programme.mention_publication_edd_classique,
                    )
                ),
                **utils.init_text_and_files_from_field(
                    self.request, self.convention.programme, "edd_stationnements"
                ),
            }
        )
        form_is_valid = self.form.is_valid()

        self.formset = LogementEDDFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_logementedd in enumerate(self.formset):
            if form_logementedd["uuid"].value():
                logementedd = LogementEDD.objects.get(
                    uuid=form_logementedd["uuid"].value()
                )
                initformset = {
                    **initformset,
                    f"form-{idx}-uuid": logementedd.uuid,
                    f"form-{idx}-designation": utils.get_form_value(
                        form_logementedd, logementedd, "designation"
                    ),
                    f"form-{idx}-financement": utils.get_form_value(
                        form_logementedd, logementedd, "financement"
                    ),
                    f"form-{idx}-numero_lot": utils.get_form_value(
                        form_logementedd, logementedd, "numero_lot"
                    ),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-designation": form_logementedd["designation"].value(),
                    f"form-{idx}-financement": form_logementedd["financement"].value(),
                    f"form-{idx}-numero_lot": form_logementedd["numero_lot"].value(),
                }
        self.formset = LogementEDDFormSet(initformset)
        self.formset.programme_id = self.convention.programme_id
        self.formset.ignore_optional_errors = self.request.POST.get(
            "ignore_optional_errors", False
        )
        formset_is_valid = self.formset.is_valid()

        if form_is_valid and formset_is_valid:
            self._save_programme_edd()
            self._save_programme_logement_edd()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_programme_edd(self):
        for lot_convention in self.convention.lots.all():
            lot_convention.edd_volumetrique = utils.set_files_and_text_field(
                self.form.cleaned_data["edd_volumetrique_files"],
                self.form.cleaned_data["edd_volumetrique"],
            )
            self.convention.programme.mention_publication_edd_volumetrique = (
                self.form.cleaned_data["mention_publication_edd_volumetrique"]
            )
            lot_convention.edd_classique = utils.set_files_and_text_field(
                self.form.cleaned_data["edd_classique_files"],
                self.form.cleaned_data["edd_classique"],
            )
            self.convention.programme.mention_publication_edd_classique = (
                self.form.cleaned_data["mention_publication_edd_classique"]
            )
            self.convention.programme.edd_stationnements = (
                utils.set_files_and_text_field(
                    self.form.cleaned_data["edd_stationnements_files"],
                    self.form.cleaned_data["edd_stationnements"],
                )
            )
            lot_convention.save()
        self.convention.programme.save()

    def _save_programme_logement_edd(self):
        lgt_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        lgt_uuids = list(filter(None, lgt_uuids1))
        self.convention.programme.logementedds.exclude(uuid__in=lgt_uuids).delete()
        for form_logementedd in self.formset:
            if form_logementedd.cleaned_data["uuid"]:
                logementedd = LogementEDD.objects.get(
                    uuid=form_logementedd.cleaned_data["uuid"]
                )
                logementedd.financement = form_logementedd.cleaned_data["financement"]
                logementedd.designation = form_logementedd.cleaned_data["designation"]
                logementedd.numero_lot = form_logementedd.cleaned_data["numero_lot"]
            else:
                logementedd = LogementEDD.objects.create(
                    programme=self.convention.programme,
                    financement=form_logementedd.cleaned_data["financement"],
                    designation=form_logementedd.cleaned_data["designation"],
                    numero_lot=form_logementedd.cleaned_data["numero_lot"],
                )
            logementedd.save()
