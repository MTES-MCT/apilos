from django.http import HttpRequest

from bailleurs.forms import BailleurForm
from conventions.models import Convention
from conventions.services import utils
from conventions.services.services_conventions import ConventionService


class ConventionBailleurService(ConventionService):
    convention: Convention
    request: HttpRequest
    form: BailleurForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    redirect_recap: bool = False

    def get(self):
        bailleurs = [(b.uuid, b.nom) for b in self.request.user.bailleurs()]
        bailleur = self.convention.bailleur
        self.form = BailleurForm(
            bailleurs,
            initial={
                "uuid": bailleur.uuid,
                "bailleur": bailleur.uuid,
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
        self.redirect_recap = bool(self.request.POST.get("redirect_to_recap", False))
        self._bailleur_atomic_update(
            self.request, self.convention, self.convention.bailleur
        )

    def _bailleur_atomic_update(self, request, convention, bailleur):
        self.form = BailleurForm(
            [],
            {
                "uuid": bailleur.uuid,
                "nom": request.POST.get("nom", bailleur.nom),
                "siret": request.POST.get("siret", bailleur.siret),
                "capital_social": request.POST.get(
                    "capital_social", bailleur.capital_social
                ),
                "adresse": request.POST.get("adresse", bailleur.adresse),
                "code_postal": request.POST.get("code_postal", bailleur.code_postal),
                "ville": request.POST.get("ville", bailleur.ville),
                "signataire_nom": request.POST.get(
                    "signataire_nom",
                    self.convention.signataire_nom or bailleur.signataire_nom,
                ),
                "signataire_fonction": request.POST.get(
                    "signataire_fonction",
                    convention.signataire_fonction or bailleur.signataire_fonction,
                ),
                "signataire_date_deliberation": request.POST.get(
                    "signataire_date_deliberation",
                    convention.signataire_date_deliberation
                    or bailleur.signataire_date_deliberation,
                ),
            },
        )
        if self.form.is_valid():
            _save_bailleur(convention, bailleur, self.form)
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
