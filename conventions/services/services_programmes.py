from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.db.models.query import QuerySet

from conventions.services.services_conventions import ConventionService
from conventions.templatetags.custom_filters import is_instructeur
from conventions.models import Convention
from conventions.forms import UploadForm
from core.services import EmailService
from instructeurs.models import Administration
from bailleurs.models import Bailleur
from programmes.models import (
    Financement,
    Programme,
    Lot,
    LogementEDD,
    ReferenceCadastrale,
    TypeOperation,
)
from programmes.subforms.lot_selection import (
    ProgrammeSelectionFromDBForm,
    ProgrammeSelectionFromZeroForm,
)
from programmes.forms import (
    ProgrammeForm,
    ProgrammeCadastralForm,
    ProgrammeEDDForm,
    LogementEDDFormSet,
    ReferenceCadastraleFormSet,
)
from . import utils
from . import upload_objects


def _get_choices_from_object(object_list):
    return [(instance.uuid, str(instance)) for instance in object_list]


class ConventionSeletionService:
    request: HttpRequest
    convention: Convention
    form: ProgrammeSelectionFromDBForm | ProgrammeSelectionFromZeroForm
    lots: QuerySet[Lot] | None = None
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def _get_bailleur_choices(self):
        return _get_choices_from_object(
            Bailleur.objects.all().order_by("nom")
            if is_instructeur(self.request)
            else self.request.user.bailleurs()
        )

    def _get_administration_choices(self):
        return _get_choices_from_object(
            self.request.user.administrations()
            if is_instructeur(self.request)
            else Administration.objects.all().order_by("nom")
        )

    def get_from_zero(self):
        self.form = ProgrammeSelectionFromZeroForm(
            bailleurs=self._get_bailleur_choices(),
            administrations=self._get_administration_choices(),
        )

    def post_from_zero(self):
        self.form = ProgrammeSelectionFromZeroForm(
            self.request.POST,
            bailleurs=self._get_bailleur_choices(),
            administrations=self._get_administration_choices(),
        )
        if self.form.is_valid():
            bailleur = Bailleur.objects.get(uuid=self.form.cleaned_data["bailleur"])
            administration = Administration.objects.get(
                uuid=self.form.cleaned_data["administration"]
            )
            programme = Programme.objects.create(
                nom=self.form.cleaned_data["nom"],
                code_postal=self.form.cleaned_data["code_postal"],
                ville=self.form.cleaned_data["ville"],
                bailleur=bailleur,
                administration=administration,
                nature_logement=self.form.cleaned_data["nature_logement"],
                type_operation=(
                    TypeOperation.SANSTRAVAUX
                    if self.form.cleaned_data["financement"]
                    == Financement.SANS_FINANCEMENT
                    else TypeOperation.NEUF
                ),
            )
            programme.save()
            lot = Lot.objects.create(
                nb_logements=self.form.cleaned_data["nb_logements"],
                financement=self.form.cleaned_data["financement"],
                type_habitat=self.form.cleaned_data["type_habitat"],
                programme=programme,
            )
            lot.save()
            self.convention = Convention.objects.create(
                lot=lot,
                programme_id=lot.programme_id,
                financement=lot.financement,
                cree_par=self.request.user,
            )
            _send_email_staff(self.request, self.convention)
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS

    def get_from_db(self):
        self.lots = (
            self.request.user.lots()
            .prefetch_related("programme")
            .prefetch_related("conventions")
            .order_by(
                "programme__ville", "programme__nom", "nb_logements", "financement"
            )
            .filter(programme__parent_id__isnull=True)
        )
        self.form = ProgrammeSelectionFromDBForm(
            lots=_get_choices_from_object(self.lots),
        )

    def post_from_db(self):
        self.lots = (
            self.request.user.lots()
            .prefetch_related("programme")
            .prefetch_related("conventions")
            .order_by(
                "programme__ville", "programme__nom", "nb_logements", "financement"
            )
            .filter(programme__parent_id__isnull=True)
        )
        self.form = ProgrammeSelectionFromDBForm(
            self.request.POST,
            lots=_get_choices_from_object(self.lots),
        )
        if self.form.is_valid():
            lot = Lot.objects.get(uuid=self.form.cleaned_data["lot"])
            lot.programme.nature_logement = self.form.cleaned_data["nature_logement"]
            lot.programme.save()
            self.convention = Convention.objects.create(
                lot=lot,
                programme_id=lot.programme_id,
                financement=lot.financement,
                cree_par=self.request.user,
            )
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS


def _send_email_staff(request, convention):
    # envoi d'un mail au staff APiLos lors de la création from scratch
    convention_url = request.build_absolute_uri(
        reverse("conventions:recapitulatif", args=[convention.uuid])
    )
    text_content = render_to_string(
        "emails/alert_create_convention.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
            "programme": convention.programme,
            "user": request.user,
        },
    )
    html_content = render_to_string(
        "emails/alert_create_convention.html",
        {
            "convention_url": convention_url,
            "convention": convention,
            "programme": convention.programme,
            "user": request.user,
        },
    )

    subject = f"[{settings.ENVIRONMENT.upper()}] "
    subject += f"Nouvelle convention créée de zéro ({convention})"
    EmailService(
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    ).send_to_devs()


class ConventionProgrammeService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ProgrammeForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False

    def get(self):
        programme = self.convention.programme
        lot = self.convention.lot
        self.form = ProgrammeForm(
            initial={
                "uuid": programme.uuid,
                "nom": programme.nom,
                "adresse": programme.adresse,
                "code_postal": programme.code_postal,
                "ville": programme.ville,
                "nb_logements": lot.nb_logements,
                "type_habitat": lot.type_habitat,
                "type_operation": programme.type_operation,
                "anru": programme.anru,
                "autres_locaux_hors_convention": programme.autres_locaux_hors_convention,
                "nb_locaux_commerciaux": programme.nb_locaux_commerciaux,
                "nb_bureaux": programme.nb_bureaux,
            }
        )

    def save(self):
        self.redirect_recap = bool(self.request.POST.get("redirect_to_recap", False))
        self._programme_atomic_update()

    def _programme_atomic_update(self):
        self.form = ProgrammeForm(
            {
                "uuid": self.convention.programme.uuid,
                "nb_logements": self.request.POST.get(
                    "nb_logements", self.convention.lot.nb_logements
                ),
                "type_habitat": self.request.POST.get(
                    "type_habitat", self.convention.lot.type_habitat
                ),
                **utils.build_partial_form(
                    self.request,
                    self.convention.programme,
                    [
                        "nom",
                        "adresse",
                        "code_postal",
                        "ville",
                        "type_operation",
                        "anru",
                        "autres_locaux_hors_convention",
                        "nb_locaux_commerciaux",
                        "nb_bureaux",
                    ],
                ),
            }
        )
        if self.form.is_valid():
            _save_programme_and_lot(
                self.convention.programme, self.convention.lot, self.form
            )
            self.return_status = utils.ReturnStatus.SUCCESS


def _save_programme_and_lot(programme, lot, form):
    programme.nom = form.cleaned_data["nom"]
    programme.adresse = form.cleaned_data["adresse"]
    programme.code_postal = form.cleaned_data["code_postal"]
    programme.ville = form.cleaned_data["ville"]
    if form.cleaned_data["type_operation"]:
        programme.type_operation = form.cleaned_data["type_operation"]
    programme.anru = form.cleaned_data["anru"]
    programme.autres_locaux_hors_convention = form.cleaned_data[
        "autres_locaux_hors_convention"
    ]
    programme.nb_locaux_commerciaux = form.cleaned_data["nb_locaux_commerciaux"]
    programme.nb_bureaux = form.cleaned_data["nb_bureaux"]
    programme.save()
    lot.nb_logements = form.cleaned_data["nb_logements"]
    lot.type_habitat = form.cleaned_data["type_habitat"]
    lot.save()


class ConventionCadastreService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ProgrammeCadastralForm
    formset: ReferenceCadastraleFormSet
    upform: UploadForm = UploadForm()
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False
    editable_after_upload: bool = False

    def get(self):
        initial = []
        referencecadastrales = (
            self.convention.programme.referencecadastrales.all().order_by("section")
        )
        for referencecadastrale in referencecadastrales:
            initial.append(
                {
                    "uuid": referencecadastrale.uuid,
                    "section": referencecadastrale.section,
                    "numero": referencecadastrale.numero,
                    "lieudit": referencecadastrale.lieudit,
                    "surface": referencecadastrale.surface,
                }
            )
        self.formset = ReferenceCadastraleFormSet(initial=initial)
        self.form = ProgrammeCadastralForm(
            initial={
                "uuid": self.convention.programme.uuid,
                "permis_construire": self.convention.programme.permis_construire,
                "date_acte_notarie": utils.format_date_for_form(
                    self.convention.programme.date_acte_notarie
                ),
                "date_achevement_previsible": utils.format_date_for_form(
                    self.convention.programme.date_achevement_previsible
                ),
                "date_achat": utils.format_date_for_form(
                    self.convention.programme.date_achat
                ),
                "date_autorisation_hors_habitat_inclusif": utils.format_date_for_form(
                    self.convention.programme.date_autorisation_hors_habitat_inclusif
                ),
                "date_convention_location": utils.format_date_for_form(
                    self.convention.programme.date_convention_location
                ),
                "date_achevement": utils.format_date_for_form(
                    self.convention.programme.date_achevement
                ),
                **utils.get_text_and_files_from_field(
                    "vendeur", self.convention.programme.vendeur
                ),
                **utils.get_text_and_files_from_field(
                    "acquereur", self.convention.programme.acquereur
                ),
                **utils.get_text_and_files_from_field(
                    "reference_notaire", self.convention.programme.reference_notaire
                ),
                **utils.get_text_and_files_from_field(
                    "reference_publication_acte",
                    self.convention.programme.reference_publication_acte,
                ),
                **utils.get_text_and_files_from_field(
                    "effet_relatif", self.convention.programme.effet_relatif
                ),
                **utils.get_text_and_files_from_field(
                    "acte_de_propriete", self.convention.programme.acte_de_propriete
                ),
                **utils.get_text_and_files_from_field(
                    "certificat_adressage",
                    self.convention.programme.certificat_adressage,
                ),
                **utils.get_text_and_files_from_field(
                    "reference_cadastrale",
                    self.convention.programme.reference_cadastrale,
                ),
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        # When the user cliked on "Téléverser" button
        if self.request.POST.get("Upload", False):
            self.form = ProgrammeCadastralForm(self.request.POST)
            self._upload_cadastre()
        # When the user cliked on "Enregistrer et Suivant"
        else:
            self._programme_cadastrale_atomic_update()

    def _upload_cadastre(self):
        self.formset = ReferenceCadastraleFormSet(self.request.POST)
        self.upform = UploadForm(self.request.POST, self.request.FILES)
        if self.upform.is_valid():
            result = upload_objects.handle_uploaded_xlsx(
                self.upform,
                self.request.FILES["file"],
                ReferenceCadastrale,
                self.convention,
                "cadastre.xlsx",
            )
            if result["success"] != utils.ReturnStatus.ERROR:
                refcads_by_section = {}
                for refcad in ReferenceCadastrale.objects.filter(
                    programme_id=self.convention.programme_id
                ):
                    refcads_by_section[
                        f"{refcad.section}__{refcad.numero}"
                    ] = refcad.uuid

                for obj in result["objects"]:
                    if (
                        "section" in obj
                        and "numero" in obj
                        and f"{obj['section']}__{obj['numero']}" in refcads_by_section
                    ):
                        obj["uuid"] = refcads_by_section[
                            f"{obj['section']}__{obj['numero']}"
                        ]

                self.formset = ReferenceCadastraleFormSet(initial=result["objects"])
                self.import_warnings = result["import_warnings"]
                self.editable_after_upload = True

    def _programme_cadastrale_atomic_update(self):
        self.form = ProgrammeCadastralForm(
            {
                "uuid": self.convention.programme.uuid,
                **utils.build_partial_form(
                    self.request,
                    self.convention.programme,
                    [
                        "permis_construire",
                        "date_acte_notarie",
                        "date_achevement_previsible",
                        "date_autorisation_hors_habitat_inclusif",
                        "date_convention_location",
                        "date_achat",
                        "date_achevement",
                    ],
                ),
                **utils.build_partial_text_and_files_form(
                    self.request,
                    self.convention.programme,
                    [
                        "vendeur",
                        "acquereur",
                        "reference_notaire",
                        "reference_publication_acte",
                        "acte_de_propriete",
                        "effet_relatif",
                        "certificat_adressage",
                        "reference_cadastrale",
                    ],
                ),
            }
        )
        form_is_valid = self.form.is_valid()

        self.formset = ReferenceCadastraleFormSet(self.request.POST)
        initformset = {
            "form-TOTAL_FORMS": self.request.POST.get(
                "form-TOTAL_FORMS", len(self.formset)
            ),
            "form-INITIAL_FORMS": self.request.POST.get(
                "form-INITIAL_FORMS", len(self.formset)
            ),
        }
        for idx, form_reference_cadastrale in enumerate(self.formset):
            if form_reference_cadastrale["uuid"].value():
                reference_cadastrale = ReferenceCadastrale.objects.get(
                    uuid=form_reference_cadastrale["uuid"].value()
                )
                initformset = {
                    **initformset,
                    f"form-{idx}-uuid": reference_cadastrale.uuid,
                    f"form-{idx}-section": utils.get_form_value(
                        form_reference_cadastrale, reference_cadastrale, "section"
                    ),
                    f"form-{idx}-numero": utils.get_form_value(
                        form_reference_cadastrale, reference_cadastrale, "numero"
                    ),
                    f"form-{idx}-lieudit": utils.get_form_value(
                        form_reference_cadastrale, reference_cadastrale, "lieudit"
                    ),
                    f"form-{idx}-surface": utils.get_form_value(
                        form_reference_cadastrale, reference_cadastrale, "surface"
                    ),
                }
            else:
                initformset = {
                    **initformset,
                    f"form-{idx}-section": form_reference_cadastrale["section"].value(),
                    f"form-{idx}-numero": form_reference_cadastrale["numero"].value(),
                    f"form-{idx}-lieudit": form_reference_cadastrale["lieudit"].value(),
                    f"form-{idx}-surface": form_reference_cadastrale["surface"].value(),
                }
        self.formset = ReferenceCadastraleFormSet(initformset)
        formset_is_valid = self.formset.is_valid()

        if form_is_valid and formset_is_valid:
            self._save_programme_cadastrale()
            self._save_programme_reference_cadastrale()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_programme_cadastrale(self):
        self.convention.programme.permis_construire = self.form.cleaned_data[
            "permis_construire"
        ]
        self.convention.programme.date_acte_notarie = self.form.cleaned_data[
            "date_acte_notarie"
        ]
        self.convention.programme.date_achevement_previsible = self.form.cleaned_data[
            "date_achevement_previsible"
        ]
        self.convention.programme.date_autorisation_hors_habitat_inclusif = (
            self.form.cleaned_data["date_autorisation_hors_habitat_inclusif"]
        )
        self.convention.programme.date_convention_location = self.form.cleaned_data[
            "date_convention_location"
        ]
        self.convention.programme.date_achat = self.form.cleaned_data["date_achat"]
        self.convention.programme.date_achevement = self.form.cleaned_data[
            "date_achevement"
        ]
        self.convention.programme.vendeur = utils.set_files_and_text_field(
            self.form.cleaned_data["vendeur_files"],
            self.form.cleaned_data["vendeur"],
        )
        self.convention.programme.acquereur = utils.set_files_and_text_field(
            self.form.cleaned_data["acquereur_files"],
            self.form.cleaned_data["acquereur"],
        )
        self.convention.programme.reference_notaire = utils.set_files_and_text_field(
            self.form.cleaned_data["reference_notaire_files"],
            self.form.cleaned_data["reference_notaire"],
        )
        self.convention.programme.reference_publication_acte = (
            utils.set_files_and_text_field(
                self.form.cleaned_data["reference_publication_acte_files"],
                self.form.cleaned_data["reference_publication_acte"],
            )
        )
        self.convention.programme.effet_relatif = utils.set_files_and_text_field(
            self.form.cleaned_data["effet_relatif_files"],
        )
        self.convention.programme.acte_de_propriete = utils.set_files_and_text_field(
            self.form.cleaned_data["acte_de_propriete_files"],
        )
        self.convention.programme.certificat_adressage = utils.set_files_and_text_field(
            self.form.cleaned_data["certificat_adressage_files"],
        )
        self.convention.programme.reference_cadastrale = utils.set_files_and_text_field(
            self.form.cleaned_data["reference_cadastrale_files"],
        )
        self.convention.programme.save()

    def _save_programme_reference_cadastrale(self):
        obj_uuids1 = list(map(lambda x: x.cleaned_data["uuid"], self.formset))
        obj_uuids = list(filter(None, obj_uuids1))
        self.convention.programme.referencecadastrales.exclude(
            uuid__in=obj_uuids
        ).delete()
        for form in self.formset:
            if form.cleaned_data["uuid"]:
                reference_cadastrale = ReferenceCadastrale.objects.get(
                    uuid=form.cleaned_data["uuid"]
                )
                reference_cadastrale.section = form.cleaned_data["section"]
                reference_cadastrale.numero = form.cleaned_data["numero"]
                reference_cadastrale.lieudit = form.cleaned_data["lieudit"]
                reference_cadastrale.surface = form.cleaned_data["surface"]
            else:
                reference_cadastrale = ReferenceCadastrale.objects.create(
                    programme=self.convention.programme,
                    section=form.cleaned_data["section"],
                    numero=form.cleaned_data["numero"],
                    lieudit=form.cleaned_data["lieudit"],
                    surface=form.cleaned_data["surface"],
                )
            reference_cadastrale.save()


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
                "lot_uuid": self.convention.lot.uuid,
                **utils.get_text_and_files_from_field(
                    "edd_volumetrique", self.convention.lot.edd_volumetrique
                ),
                "mention_publication_edd_volumetrique": (
                    self.convention.programme.mention_publication_edd_volumetrique
                ),
                **utils.get_text_and_files_from_field(
                    "edd_classique", self.convention.lot.edd_classique
                ),
                "mention_publication_edd_classique": (
                    self.convention.programme.mention_publication_edd_classique
                ),
            }
        )

    def save(self):
        self.editable_after_upload = self.request.POST.get(
            "editable_after_upload", False
        )
        # When the user cliked on "Téléverser" button
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
                    self.request, self.convention.lot, "edd_volumetrique"
                ),
                "mention_publication_edd_volumetrique": (
                    self.request.POST.get(
                        "mention_publication_edd_volumetrique",
                        self.convention.programme.mention_publication_edd_volumetrique,
                    )
                ),
                **utils.init_text_and_files_from_field(
                    self.request, self.convention.lot, "edd_classique"
                ),
                "mention_publication_edd_classique": (
                    self.request.POST.get(
                        "mention_publication_edd_classique",
                        self.convention.programme.mention_publication_edd_classique,
                    )
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
        self.convention.lot.edd_volumetrique = utils.set_files_and_text_field(
            self.form.cleaned_data["edd_volumetrique_files"],
            self.form.cleaned_data["edd_volumetrique"],
        )
        self.convention.programme.mention_publication_edd_volumetrique = (
            self.form.cleaned_data["mention_publication_edd_volumetrique"]
        )
        self.convention.lot.edd_classique = utils.set_files_and_text_field(
            self.form.cleaned_data["edd_classique_files"],
            self.form.cleaned_data["edd_classique"],
        )
        self.convention.programme.mention_publication_edd_classique = (
            self.form.cleaned_data["mention_publication_edd_classique"]
        )
        self.convention.lot.save()
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
