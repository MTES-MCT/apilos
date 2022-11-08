from django.db import transaction
from django.http import HttpRequest

from bailleurs.forms import BailleurForm, UpdateBailleurForm
from bailleurs.models import Bailleur
from conventions.models import Convention, ConventionStatut
from conventions.services import utils
from conventions.services.services_conventions import ConventionService
from programmes.models import Programme


class ConventionBailleurService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: BailleurForm
    upform: UpdateBailleurForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False

    def get(self):
        bailleur = self.convention.programme.bailleur
        # Check if programme has validated convention
        convention_validee = [
            programme_convention
            for programme_convention in self.convention.programme.conventions.all()
            if programme_convention.statut
            in [
                ConventionStatut.A_SIGNER,
                ConventionStatut.SIGNEE,
            ]
        ]
        bailleurs = (
            []
            if convention_validee
            else [(b.uuid, b.nom) for b in self.request.user.bailleurs(full_scope=True)]
        )
        self.upform = UpdateBailleurForm(
            bailleurs=bailleurs,
            initial={"bailleur": bailleur.uuid},
        )
        self.form = BailleurForm(
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
            },
        )

    def save(self):
        self.form = BailleurForm(self.request.POST)

        self.upform = UpdateBailleurForm(
            self.request.POST,
            bailleurs=[
                (b.uuid, b.nom) for b in self.request.user.bailleurs(full_scope=True)
            ],
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
            bailleur = Bailleur.objects.get(uuid=self.request.POST["bailleur"])
            programme = (
                Programme.objects.prefetch_related("lot_set__logements__annexes")
                .prefetch_related("lot_set__type_stationnements")
                .prefetch_related("logementedd_set")
                .prefetch_related("conventions__pret_set")
                .prefetch_related("referencecadastrale_set")
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
        self.form = BailleurForm(
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
            },
        )

        if self.form.is_valid():
            _save_bailleur(self.convention, bailleur, self.form)
            self.return_status = utils.ReturnStatus.SUCCESS


def _save_bailleur(convention, bailleur, form):
    bailleur.nom = form.cleaned_data["nom"]
    bailleur.siret = form.cleaned_data["siret"]
    bailleur.capital_social = form.cleaned_data["capital_social"]
    bailleur.adresse = form.cleaned_data["adresse"]
    bailleur.code_postal = form.cleaned_data["code_postal"]
    bailleur.ville = form.cleaned_data["ville"]
    bailleur.save()
    convention.signataire_nom = form.cleaned_data["signataire_nom"]
    convention.signataire_fonction = form.cleaned_data["signataire_fonction"]
    convention.signataire_date_deliberation = form.cleaned_data[
        "signataire_date_deliberation"
    ]
    convention.save()
