import datetime

from conventions.forms import ConventionFinancementForm, PretFormSet
from conventions.forms.upload import UploadForm
from conventions.models.pret import Pret
from conventions.services import upload_objects, utils
from conventions.services.conventions import ConventionService


class ConventionFinancementService(ConventionService):
    form: ConventionFinancementForm
    upform: UploadForm = UploadForm()

    def get(self):
        initial = []
        for pret in self.convention.lot.prets.all():
            initial.append(
                {
                    "uuid": pret.uuid,
                    "numero": pret.numero,
                    "date_octroi": utils.format_date_for_form(pret.date_octroi),
                    "duree": pret.duree,
                    "montant": pret.montant,
                    "preteur": pret.preteur,
                    "autre": pret.autre,
                }
            )
        self.formset = PretFormSet(initial=initial)
        self.form = ConventionFinancementForm(
            initial={
                "uuid": self.convention.uuid,
                "annee_fin_conventionnement": (
                    str(self.convention.date_fin_conventionnement.year)
                    if self.convention.date_fin_conventionnement is not None
                    else None
                ),
                "fond_propre": self.convention.fond_propre,
                "historique_financement_public": self.convention.historique_financement_public,
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        # When the user cliked on "Déposer" button
        if self.request.POST.get("Upload", False):
            self.form = ConventionFinancementForm(initial=self.request.POST)
            self._upload_prets()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._convention_financement_atomic_update()

    def _add_uuid_to_prets(self, result):
        prets_by_numero = {}
        for pret in self.convention.lot.prets.all():
            prets_by_numero[pret.numero] = pret.uuid
        for obj in result["objects"]:
            if "numero" in obj and obj["numero"] in prets_by_numero:
                obj["uuid"] = prets_by_numero[obj["numero"]]
        return result

    def _upload_prets(self):
        self.formset = PretFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():

            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                Pret,
                self.convention,
                "financement.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                result = self._add_uuid_to_prets(result=result)

                self.formset = PretFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True
                if not self.formset.validate_initial_numero_unicity():
                    self.import_warnings.append(
                        "Merci d'utiliser des numéros de financements différents."
                    )

    def _convention_financement_atomic_update(self):
        self.form = ConventionFinancementForm(
            {
                "uuid": self.convention.uuid,
                "fond_propre": self.request.POST.get(
                    "fond_propre", self.convention.fond_propre
                ),
                "historique_financement_public": self.request.POST.get(
                    "historique_financement_public",
                    self.convention.historique_financement_public,
                ),
                "annee_fin_conventionnement": self.request.POST.get(
                    "annee_fin_conventionnement",
                    (
                        self.convention.date_fin_conventionnement.year
                        if self.convention.date_fin_conventionnement is not None
                        else None
                    ),
                ),
            }
        )

        self.formset = PretFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_pret in enumerate(self.formset):
            if form_pret["uuid"].value():
                pret = Pret.objects.get(uuid=form_pret["uuid"].value())
                initformset = {
                    **initformset,
                    f"form-{idx}-uuid": pret.uuid,
                    f"form-{idx}-numero": utils.get_form_value(
                        form_pret, pret, "numero"
                    ),
                    f"form-{idx}-date_octroi": utils.get_form_date_value(
                        form_pret, pret, "date_octroi"
                    ),
                    f"form-{idx}-duree": utils.get_form_value(form_pret, pret, "duree"),
                    f"form-{idx}-montant": utils.get_form_value(
                        form_pret, pret, "montant"
                    ),
                    f"form-{idx}-preteur": utils.get_form_value(
                        form_pret, pret, "preteur"
                    ),
                    f"form-{idx}-autre": utils.get_form_value(form_pret, pret, "autre"),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-numero": form_pret["numero"].value(),
                    f"form-{idx}-date_octroi": form_pret["date_octroi"].value(),
                    f"form-{idx}-duree": form_pret["duree"].value(),
                    f"form-{idx}-montant": form_pret["montant"].value(),
                    f"form-{idx}-preteur": form_pret["preteur"].value(),
                    f"form-{idx}-autre": form_pret["autre"].value(),
                }
        self.formset = PretFormSet(initformset)
        self.formset.convention = self.convention

        if self.formset.is_valid():
            self.form.prets = self.formset
            self.form.convention = self.convention
            if self.form.is_valid():
                self._save_convention_financement()
                self._save_convention_financement_prets()
                self.return_status = utils.ReturnStatus.SUCCESS
                self.redirect_recap = self.request.POST.get("redirect_to_recap", False)

    def _save_convention_financement(self):
        if (
            self.convention.programme.is_foyer()
            or self.convention.programme.is_residence()
        ):
            self.convention.date_fin_conventionnement = datetime.date(
                self.form.cleaned_data["annee_fin_conventionnement"], 12, 31
            )
        else:
            self.convention.date_fin_conventionnement = datetime.date(
                self.form.cleaned_data["annee_fin_conventionnement"], 6, 30
            )
        self.convention.fond_propre = self.form.cleaned_data["fond_propre"]
        self.convention.historique_financement_public = self.form.cleaned_data[
            "historique_financement_public"
        ]
        self.convention.save()

    def _save_convention_financement_prets(self):
        obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        obj_uuids = list(filter(None, obj_uuids1))
        self.convention.lot.prets.exclude(uuid__in=obj_uuids).delete()
        for form_pret in self.formset:
            if form_pret.cleaned_data["uuid"]:
                pret = Pret.objects.get(uuid=form_pret.cleaned_data["uuid"])
                pret.numero = form_pret.cleaned_data["numero"]
                pret.date_octroi = form_pret.cleaned_data["date_octroi"]
                pret.duree = form_pret.cleaned_data["duree"]
                pret.montant = form_pret.cleaned_data["montant"]
                pret.preteur = form_pret.cleaned_data["preteur"]
                pret.autre = form_pret.cleaned_data["autre"]

            else:
                pret = Pret.objects.create(
                    lot=self.convention.lot,
                    numero=form_pret.cleaned_data["numero"],
                    date_octroi=form_pret.cleaned_data["date_octroi"],
                    duree=form_pret.cleaned_data["duree"],
                    montant=form_pret.cleaned_data["montant"],
                    preteur=form_pret.cleaned_data["preteur"],
                    autre=form_pret.cleaned_data["autre"],
                )
            pret.save()
