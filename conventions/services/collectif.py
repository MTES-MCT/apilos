from conventions.forms import LocauxCollectifsFormSet, LotCollectifForm, UploadForm
from conventions.services.conventions import ConventionService
from programmes.models import LocauxCollectifs

from . import upload_objects, utils


class ConventionCollectifService(ConventionService):
    form: LotCollectifForm
    formset: LocauxCollectifsFormSet
    upform: UploadForm = UploadForm()

    def get(self):
        initial = []
        locaux_collectifs = LocauxCollectifs.objects.filter(
            lot_id=self.convention.lot.id
        )
        for type_locaux_collectifs in locaux_collectifs:
            initial.append(
                {
                    "uuid": type_locaux_collectifs.uuid,
                    "type_local": type_locaux_collectifs.type_local,
                    "surface_habitable": type_locaux_collectifs.surface_habitable,
                    "nombre": type_locaux_collectifs.nombre,
                }
            )
        self.formset = LocauxCollectifsFormSet(initial=initial)
        lot = self.convention.lot
        self.form = LotCollectifForm(
            initial={
                "uuid": lot.uuid,
                "foyer_residence_nb_garage_parking": lot.foyer_residence_nb_garage_parking,
                "foyer_residence_dependance": lot.foyer_residence_dependance,
                "foyer_residence_locaux_hors_convention": (
                    lot.foyer_residence_locaux_hors_convention
                ),
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        if self.request.POST.get("Upload", False):
            self.form = LotCollectifForm(self.request.POST)
            self._upload_locaux_collectifs()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._collectif_atomic_update()

    def _upload_locaux_collectifs(self):
        self.formset = LocauxCollectifsFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                LocauxCollectifs,
                self.convention,
                "locaux_collectifs.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                self.formset = LocauxCollectifsFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _collectif_atomic_update(self):
        self.form = LotCollectifForm(
            {
                "uuid": self.convention.lot.uuid,
                **utils.build_partial_form(
                    self.request,
                    self.convention.lot,
                    [
                        "foyer_residence_nb_garage_parking",
                        "foyer_residence_dependance",
                        "foyer_residence_locaux_hors_convention",
                    ],
                ),
            }
        )
        form_is_valid = self.form.is_valid()

        self.formset = LocauxCollectifsFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_locaux_collectif in enumerate(self.formset):
            if form_locaux_collectif["uuid"].value():
                form_locaux_collectif = LocauxCollectifs.objects.get(
                    uuid=form_locaux_collectif["uuid"].value()
                )
                initformset = {
                    **initformset,
                    f"form-{idx}-uuid": form_locaux_collectif.uuid,
                    f"form-{idx}-type_local": utils.get_form_value(
                        form_locaux_collectif, self.convention.lot, "type_local"
                    ),
                    f"form-{idx}-surface_habitable": utils.get_form_value(
                        form_locaux_collectif,
                        form_locaux_collectif,
                        "surface_habitable",
                    ),
                    f"form-{idx}-nombre": utils.get_form_value(
                        form_locaux_collectif, form_locaux_collectif, "nombre"
                    ),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-type_local": form_locaux_collectif[
                        "type_local"
                    ].value(),
                    f"form-{idx}-surface_habitable": form_locaux_collectif[
                        "surface_habitable"
                    ].value(),
                    f"form-{idx}-nombre": form_locaux_collectif["nombre"].value(),
                }
        self.formset = LocauxCollectifsFormSet(initformset)
        formset_is_valid = self.formset.is_valid()

        if form_is_valid and formset_is_valid:
            self._save_lot_collectif()
            self._save_locaux_collectifs()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_locaux_collectifs(self):
        # obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        # obj_uuids = list(filter(None, obj_uuids1))
        obj_uuids = [
            form.cleaned_data["uuid"]
            for form in self.formset
            if form.cleaned_data["uuid"] is not None
        ]
        LocauxCollectifs.objects.filter(lot_id=self.convention.lot.id).exclude(
            uuid__in=obj_uuids
        ).delete()
        for form_locaux_collectifs in self.formset:
            if form_locaux_collectifs.cleaned_data["uuid"]:
                locaux_collectifs = LocauxCollectifs.objects.get(
                    uuid=form_locaux_collectifs.cleaned_data["uuid"]
                )
                locaux_collectifs.type_local = form_locaux_collectifs.cleaned_data[
                    "type_local"
                ]
                locaux_collectifs.surface_habitable = (
                    form_locaux_collectifs.cleaned_data["surface_habitable"]
                )
                locaux_collectifs.nombre = form_locaux_collectifs.cleaned_data["nombre"]

            else:
                locaux_collectifs = LocauxCollectifs.objects.create(
                    lot=self.convention.lot,
                    type_local=form_locaux_collectifs.cleaned_data["type_local"],
                    surface_habitable=form_locaux_collectifs.cleaned_data[
                        "surface_habitable"
                    ],
                    nombre=form_locaux_collectifs.cleaned_data["nombre"],
                )
            locaux_collectifs.save()

    def _save_lot_collectif(self):
        lot = self.convention.lot
        lot.foyer_residence_nb_garage_parking = self.form.cleaned_data[
            "foyer_residence_nb_garage_parking"
        ]
        lot.foyer_residence_dependance = self.form.cleaned_data[
            "foyer_residence_dependance"
        ]
        lot.foyer_residence_locaux_hors_convention = self.form.cleaned_data[
            "foyer_residence_locaux_hors_convention"
        ]
        lot.save()
