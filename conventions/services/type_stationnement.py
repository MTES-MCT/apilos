from django.http import HttpRequest

from conventions.forms import (
    BaseTypeStationnementFormSet,
    TypeStationnementFormSet,
    UploadForm,
)
from conventions.models import Convention
from conventions.services.conventions import ConventionService
from programmes.models import TypeStationnement

from . import upload_objects, utils


class ConventionTypeStationnementService(ConventionService):
    convention: Convention
    request: HttpRequest
    formset: BaseTypeStationnementFormSet
    upform: UploadForm = UploadForm()
    editable_after_upload: bool
    redirect_recap: bool = False
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    import_warnings: None | list = None

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
        # When the user cliked on "Déposer" button
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
