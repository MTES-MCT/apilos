from django.conf import settings
from django.db import transaction
from django.http import HttpRequest

from conventions.forms import ConventionBailleurForm, ChangeBailleurForm
from bailleurs.models import Bailleur
from conventions.models import Convention, ConventionStatut
from conventions.services import utils
from conventions.services.conventions import ConventionService
from programmes.models import Programme


class ConventionBailleurService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: ConventionBailleurForm
    upform: ChangeBailleurForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False

    def get(self):
        bailleur = self.convention.programme.bailleur

        self.upform = ChangeBailleurForm(
            bailleur_query=self.request.user.bailleurs(full_scope=True)[
                : settings.APILOS_MAX_DROPDOWN_COUNT
            ],
            initial={"bailleur": bailleur},
        )
        self.form = ConventionBailleurForm(
            initial={
                "uuid": bailleur.uuid,
                "nom": bailleur.nom,
                "siret": bailleur.siret,
                "capital_social": bailleur.capital_social,
                "adresse": bailleur.adresse,
                "code_postal": bailleur.code_postal,
                "ville": bailleur.ville,
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
            },
        )

    def save(self):
        self.form = ConventionBailleurForm(self.request.POST)

        self.upform = ChangeBailleurForm(
            self.request.POST,
            bailleur_query=self.request.user.bailleurs(full_scope=True).filter(
                uuid=self.request.POST.get("bailleur")
            ),
        )
        update_bailleur = bool(self.request.POST.get("update_bailleur", False))
        if update_bailleur:
            self._update_bailleur()
        else:
            self.redirect_recap = bool(
                self.request.POST.get("redirect_to_recap", False)
            )
            self._bailleur_atomic_update()

    def _update_bailleur(self):
        if self.upform.is_valid():
            bailleur = self.upform.cleaned_data["bailleur"]
            programme = (
                Programme.objects.prefetch_related("lots__logements__annexes")
                .prefetch_related("lots__type_stationnements")
                .prefetch_related("logementedds")
                .prefetch_related("conventions__prets")
                .prefetch_related("referencecadastrales")
            ).get(id=self.convention.programme_id)
            for convention in programme.conventions.all():
                if convention.statut in [
                    ConventionStatut.A_SIGNER,
                    ConventionStatut.SIGNEE,
                ]:
                    raise Exception(
                        "It is not possible to update bailleur of the programme"
                        + " because some convention are validated"
                    )

            with transaction.atomic():
                programme.bailleur = bailleur
                programme.save()

            self.return_status = utils.ReturnStatus.REFRESH

    def _bailleur_atomic_update(self):
        bailleur = self.convention.programme.bailleur
        self.form = ConventionBailleurForm(
            {
                "uuid": bailleur.uuid,
                "nom": self.request.POST.get("nom", bailleur.nom),
                "siret": self.request.POST.get("siret", bailleur.siret),
                "capital_social": self.request.POST.get(
                    "capital_social", bailleur.capital_social
                ),
                "adresse": self.request.POST.get("adresse", bailleur.adresse),
                "code_postal": self.request.POST.get(
                    "code_postal", bailleur.code_postal
                ),
                "ville": self.request.POST.get("ville", bailleur.ville),
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
            self._save_bailleur()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_bailleur(self):
        bailleur = self.convention.programme.bailleur
        bailleur.nom = self.form.cleaned_data["nom"]
        bailleur.siret = self.form.cleaned_data["siret"]
        bailleur.capital_social = self.form.cleaned_data["capital_social"]
        bailleur.adresse = self.form.cleaned_data["adresse"]
        bailleur.code_postal = self.form.cleaned_data["code_postal"]
        bailleur.ville = self.form.cleaned_data["ville"]
        bailleur.save()
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
