from django.conf import settings

from bailleurs.models import Bailleur
from conventions.forms import ChangeBailleurForm, ConventionBailleurForm
from conventions.forms.convention_form_administration import (
    UpdateConventionAdministrationForm,
)
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionBailleurService(ConventionService):
    form: ConventionBailleurForm
    extra_forms: dict[
        str, ChangeBailleurForm | UpdateConventionAdministrationForm | None
    ] = {"bailleur_form": None, "administration_form": None}

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

    def get(self):
        bailleur = self.convention.programme.bailleur

        self.extra_forms["bailleur_form"] = ChangeBailleurForm(
            bailleur_query=self._get_bailleur_query(bailleur.uuid),
            initial={"bailleur": bailleur},
        )
        self.extra_forms["administration_form"] = UpdateConventionAdministrationForm(
            administrations_queryset=self.request.user.administrations(),
            initial={"administration": self.convention.administration},
        )
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
            )
        }

    def change_bailleur(self):
        self._init_forms()
        self._update_bailleur()

    def update_bailleur(self):
        self._init_forms()
        self._bailleur_atomic_update()

    def _update_bailleur(self):
        bailleur_form = self.extra_forms["bailleur_form"]
        if bailleur_form.is_valid():
            bailleur = bailleur_form.cleaned_data["bailleur"]
            self.convention.programme.bailleur = bailleur
            self.convention.programme.save()
            self.return_status = utils.ReturnStatus.REFRESH
        else:
            bailleur_form.declared_fields[
                "bailleur"
            ].queryset = self.request.user.bailleurs(full_scope=True)[
                : settings.APILOS_MAX_DROPDOWN_COUNT
            ] | Bailleur.objects.filter(
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
        self.convention.save()
