from bailleurs.forms import BailleurForm
from conventions.models import Convention
from . import utils


def bailleur_update(request, convention_uuid):
    convention = Convention.objects.prefetch_related("bailleur").get(
        uuid=convention_uuid
    )
    bailleur = convention.bailleur
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("UpdateAtomic", False):
            return _bailleur_atomic_update(request, convention, bailleur)
        form = BailleurForm(request.POST)
        if form.is_valid():
            _save_bailleur(bailleur, form)
            # All is OK -> Next:
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": convention,
            }
    else:  # GET
        request.user.check_perm("convention.view_convention", convention)
        form = BailleurForm(
            initial={
                "uuid": bailleur.uuid,
                "nom": bailleur.nom,
                "siret": bailleur.siret,
                "capital_social": bailleur.capital_social,
                "adresse": bailleur.adresse,
                "code_postal": bailleur.code_postal,
                "ville": bailleur.ville,
                "signataire_nom": bailleur.signataire_nom,
                "signataire_fonction": bailleur.signataire_fonction,
                "signataire_date_deliberation": utils.format_date_for_form(
                    bailleur.signataire_date_deliberation
                ),
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
    }


def _bailleur_atomic_update(request, convention, bailleur):
    form = BailleurForm(
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
                "signataire_nom", bailleur.signataire_nom
            ),
            "signataire_fonction": request.POST.get(
                "signataire_fonction", bailleur.signataire_fonction
            ),
            "signataire_date_deliberation": request.POST.get(
                "signataire_date_deliberation", bailleur.signataire_date_deliberation
            ),
        }
    )
    if form.is_valid():
        _save_bailleur(bailleur, form)
        return utils.base_response_redirect_recap_success(convention)
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
    }


def _save_bailleur(bailleur, form):
    bailleur.nom = form.cleaned_data["nom"]
    bailleur.siret = form.cleaned_data["siret"]
    bailleur.capital_social = form.cleaned_data["capital_social"]
    bailleur.adresse = form.cleaned_data["adresse"]
    bailleur.code_postal = form.cleaned_data["code_postal"]
    bailleur.ville = form.cleaned_data["ville"]
    bailleur.signataire_nom = form.cleaned_data["signataire_nom"]
    bailleur.signataire_fonction = form.cleaned_data["signataire_fonction"]
    bailleur.signataire_date_deliberation = form.cleaned_data[
        "signataire_date_deliberation"
    ]
    bailleur.save()
