from django.conf import settings

from bailleurs.models import Bailleur
from conventions.forms import ChangeBailleurForm, ConventionBailleurForm
from conventions.forms.convention_form_administration import ChangeAdministrationForm
from conventions.models.convention import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService
from instructeurs.models import Administration
from programmes.models import Programme


class ConventionBailleurService(ConventionService):
    form: ConventionBailleurForm
    extra_forms: dict[str, ChangeBailleurForm | ChangeAdministrationForm | None] = {
        "bailleur_form": None,
        "administration_form": None,
    }
    upform: ChangeBailleurForm | None

    def should_add_sirens(self, habilitation):
        if (
            habilitation["groupe"]["profil"]["code"] != "MO_PERS_MORALE"
            or habilitation["statut"] != "VALIDEE"
        ):
            return False
        try:
            region_code = habilitation["porteeTerritComp"]["regComp"]["code"]
        except (KeyError, TypeError):
            region_code = None
        return (
            region_code is None
            or region_code == self.convention.programme.code_insee_region
        )

    def _get_bailleur_query(self, bailleur_uuid: str):
        if self.request.user.is_cerbere_user() and self.request.user.is_bailleur():
            sirens = []
            for habilitation in self.request.session["habilitations"]:
                if self.should_add_sirens(habilitation):
                    sirens.append(habilitation["entiteMorale"]["siren"])
            return Bailleur.objects.filter(siren__in=sirens)
        return (
            self.request.user.bailleurs(full_scope=True).filter(uuid=bailleur_uuid)
            | self.request.user.bailleurs(full_scope=True)[
                : settings.APILOS_MAX_DROPDOWN_COUNT
            ]
        )

    def _get_administration_query(self, administration_uuid: str):
        return (
            self.request.user.administrations(full_scope=True).filter(
                uuid=administration_uuid
            )
            | self.request.user.administrations(full_scope=True)[
                : settings.APILOS_MAX_DROPDOWN_COUNT
            ]
        )

    def get(self):
        bailleur = self.convention.programme.bailleur
        self._initial_change_bailleur_form(bailleur)
        self._initial_change_administration_form(self.convention.administration)
        self._initial_bailleur_form(bailleur)

    def save(self):
        pass

    def _initial_change_bailleur_form(self, bailleur: Bailleur):
        self.extra_forms["bailleur_form"] = ChangeBailleurForm(
            bailleur_query=self._get_bailleur_query(bailleur.uuid),
            initial={"bailleur": bailleur},
        )

    def _initial_change_administration_form(self, administration: Administration):
        self.extra_forms["administration_form"] = ChangeAdministrationForm(
            administrations_queryset=self._get_administration_query(
                administration.uuid
            ),
            initial={"administration": administration},
        )

    def _initial_bailleur_form(self, bailleur: Bailleur):
        self.form = ConventionBailleurForm(
            initial={
                "uuid": bailleur.uuid,
                "signataire_nom": self.convention.signataire_nom
                or bailleur.signataire_nom,
                "signataire_fonction": self.convention.signataire_fonction
                or bailleur.signataire_fonction,
                "signataire_date_deliberation": utils.format_date_for_form(
                    self.convention.signataire_date_deliberation
                    or bailleur.signataire_date_deliberation
                ),
                "signataire_bloc_signature": self.convention.signataire_bloc_signature
                or bailleur.signataire_bloc_signature,
                "identification_bailleur": self.convention.identification_bailleur,
                "identification_bailleur_detail": self.convention.identification_bailleur_detail,
                "gestionnaire": self.convention.gestionnaire,
                "gestionnaire_signataire_nom": (
                    self.convention.gestionnaire_signataire_nom
                ),
                "gestionnaire_signataire_fonction": (
                    self.convention.gestionnaire_signataire_fonction
                ),
                "gestionnaire_signataire_date_deliberation": utils.format_date_for_form(
                    self.convention.gestionnaire_signataire_date_deliberation
                ),
                "gestionnaire_signataire_bloc_signature": (
                    self.convention.gestionnaire_signataire_bloc_signature
                ),
                "gestionnaire_bloc_info_complementaire": (
                    self.convention.gestionnaire_bloc_info_complementaire
                ),
                "administration": self.convention.administration,
            },
        )

    def _init_forms(self):
        self.form = ConventionBailleurForm(self.request.POST)

        self.extra_forms = {
            "bailleur_form": ChangeBailleurForm(
                self.request.POST,
                bailleur_query=self._get_bailleur_query(
                    self.request.POST.get("bailleur") or None
                ),
            ),
            "administration_form": ChangeAdministrationForm(
                self.request.POST,
                administrations_queryset=self._get_administration_query(
                    self.request.POST.get("administration") or None
                ),
            ),
        }

    def change_bailleur(self):
        self._init_forms()
        self._change_bailleur()

    def change_administration(self):
        self._init_forms()
        self._change_administration()

    def _change_administration(self):
        form = self.extra_forms["administration_form"]

        if form and form.is_valid():
            if self.convention.parent:
                convention = Convention.objects.get(id=self.convention.parent.id)
            else:
                convention = self.convention

            new_administration = form.cleaned_data["administration"]
            avenants_to_updates = convention.avenants.all()
            conventions_to_update = [convention, *avenants_to_updates]

            Programme.objects.filter(conventions__in=conventions_to_update).update(
                administration=new_administration
            )
            self.return_status = utils.ReturnStatus.SUCCESS

    def update_bailleur(self):
        self._init_forms()
        self._bailleur_atomic_update()

    def _change_bailleur(self):
        form = self.extra_forms["bailleur_form"]

        if form and form.is_valid():
            bailleur = form.cleaned_data["bailleur"]
            self.convention.programme.bailleur = bailleur
            self.convention.programme.save()
            self.return_status = utils.ReturnStatus.REFRESH
        elif form:
            form.declared_fields["bailleur"].queryset = self.request.user.bailleurs(
                full_scope=True
            )[: settings.APILOS_MAX_DROPDOWN_COUNT] | Bailleur.objects.filter(
                uuid=self.request.POST.get("bailleur") or None
            )

    def _bailleur_atomic_update(self):
        bailleur = self.convention.programme.bailleur
        self.form = ConventionBailleurForm(
            {
                # FIXME : uuid needed ?
                "uuid": bailleur.uuid,
                "signataire_nom": self.request.POST.get(
                    "signataire_nom",
                    self.convention.signataire_nom or bailleur.signataire_nom,
                ),
                "signataire_fonction": self.request.POST.get(
                    "signataire_fonction",
                    self.convention.signataire_fonction or bailleur.signataire_fonction,
                ),
                "signataire_date_deliberation": self.request.POST.get(
                    "signataire_date_deliberation",
                    self.convention.signataire_date_deliberation
                    or bailleur.signataire_date_deliberation,
                ),
                "signataire_bloc_signature": self.request.POST.get(
                    "signataire_bloc_signature",
                    self.convention.signataire_bloc_signature
                    or bailleur.signataire_bloc_signature,
                ),
                "identification_bailleur": self.request.POST.get(
                    "identification_bailleur", False
                ),
                "identification_bailleur_detail": self.request.POST.get(
                    "identification_bailleur_detail",
                    self.convention.identification_bailleur_detail,
                ),
                "gestionnaire": self.request.POST.get(
                    "gestionnaire", self.convention.gestionnaire
                ),
                "gestionnaire_signataire_nom": self.request.POST.get(
                    "gestionnaire_signataire_nom",
                    self.convention.gestionnaire_signataire_nom,
                ),
                "gestionnaire_signataire_fonction": self.request.POST.get(
                    "gestionnaire_signataire_fonction",
                    self.convention.gestionnaire_signataire_fonction,
                ),
                "gestionnaire_signataire_date_deliberation": self.request.POST.get(
                    "gestionnaire_signataire_date_deliberation",
                    self.convention.gestionnaire_signataire_date_deliberation,
                ),
                "gestionnaire_signataire_bloc_signature": self.request.POST.get(
                    "gestionnaire_signataire_bloc_signature",
                    self.convention.gestionnaire_signataire_bloc_signature,
                ),
                "gestionnaire_bloc_info_complementaire": self.request.POST.get(
                    "gestionnaire_bloc_info_complementaire",
                    self.convention.gestionnaire_bloc_info_complementaire,
                ),
            },
        )
        if self.form.is_valid():
            self._save_convention_signataire()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_convention_signataire(self):
        self.convention.signataire_nom = self.form.cleaned_data["signataire_nom"]
        self.convention.signataire_fonction = self.form.cleaned_data[
            "signataire_fonction"
        ]
        self.convention.signataire_date_deliberation = self.form.cleaned_data[
            "signataire_date_deliberation"
        ]
        self.convention.signataire_bloc_signature = self.form.cleaned_data[
            "signataire_bloc_signature"
        ]
        self.convention.identification_bailleur = self.form.cleaned_data[
            "identification_bailleur"
        ]
        self.convention.identification_bailleur_detail = self.form.cleaned_data[
            "identification_bailleur_detail"
        ]
        self.convention.gestionnaire = self.form.cleaned_data["gestionnaire"]
        self.convention.gestionnaire_signataire_nom = self.form.cleaned_data[
            "gestionnaire_signataire_nom"
        ]
        self.convention.gestionnaire_signataire_fonction = self.form.cleaned_data[
            "gestionnaire_signataire_fonction"
        ]
        self.convention.gestionnaire_signataire_date_deliberation = (
            self.form.cleaned_data["gestionnaire_signataire_date_deliberation"]
        )
        self.convention.gestionnaire_signataire_bloc_signature = self.form.cleaned_data[
            "gestionnaire_signataire_bloc_signature"
        ]
        self.convention.gestionnaire_bloc_info_complementaire = self.form.cleaned_data[
            "gestionnaire_bloc_info_complementaire"
        ]
        self.convention.save()
