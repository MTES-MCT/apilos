from bailleurs.forms import BailleurForm
from conventions.models import Convention
from . import utils


def bailleur_update(request, convention_uuid):
    convention = Convention.objects.prefetch_related("bailleur").get(
        uuid=convention_uuid
    )
    bailleur = convention.bailleur
    if request.method == "POST":
        if request.POST.get("UpdateAtomic", False):
            form = BailleurForm(
                {
                    "uuid": bailleur.uuid,
                    "nom": request.POST.get("nom", bailleur.nom),
                    "siret": request.POST.get("siret", bailleur.siret),
                    "capital_social": request.POST.get(
                        "capital_social", bailleur.capital_social
                    ),
                    "adresse": request.POST.get("adresse", bailleur.adresse),
                    "code_postal": request.POST.get(
                        "code_postal", bailleur.code_postal
                    ),
                    "ville": request.POST.get("ville", bailleur.ville),
                    "dg_nom": request.POST.get("dg_nom", bailleur.dg_nom),
                    "dg_fonction": request.POST.get(
                        "dg_fonction", bailleur.dg_fonction
                    ),
                    "dg_date_deliberation": request.POST.get(
                        "dg_date_deliberation", bailleur.dg_date_deliberation
                    ),
                }
            )
            if form.is_valid():
                bailleur.nom = form.cleaned_data["nom"]
                bailleur.siret = form.cleaned_data["siret"]
                bailleur.capital_social = form.cleaned_data["capital_social"]
                bailleur.adresse = form.cleaned_data["adresse"]
                bailleur.code_postal = form.cleaned_data["code_postal"]
                bailleur.ville = form.cleaned_data["ville"]
                bailleur.dg_nom = form.cleaned_data["dg_nom"]
                bailleur.dg_fonction = form.cleaned_data["dg_fonction"]
                bailleur.dg_date_deliberation = form.cleaned_data[
                    "dg_date_deliberation"
                ]
                bailleur.save()
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "comments": convention.get_comments_dict(),
                    "redirect": "recapitulatif",
                }
        else:
            request.user.check_perm("convention.change_convention", convention)
            form = BailleurForm(request.POST)
            if form.is_valid():
                bailleur.nom = form.cleaned_data["nom"]
                bailleur.siret = form.cleaned_data["siret"]
                bailleur.capital_social = form.cleaned_data["capital_social"]
                bailleur.adresse = form.cleaned_data["adresse"]
                bailleur.code_postal = form.cleaned_data["code_postal"]
                bailleur.ville = form.cleaned_data["ville"]
                bailleur.dg_nom = form.cleaned_data["dg_nom"]
                bailleur.dg_fonction = form.cleaned_data["dg_fonction"]
                bailleur.dg_date_deliberation = form.cleaned_data[
                    "dg_date_deliberation"
                ]
                bailleur.save()
                # All is OK -> Next:
                return {
                    "success": utils.ReturnStatus.SUCCESS,
                    "convention": convention,
                    "form": form,
                }
    # If this is a GET (or any other method) create the default form.
    else:
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
                "dg_nom": bailleur.dg_nom,
                "dg_fonction": bailleur.dg_fonction,
                "dg_date_deliberation": utils.format_date_for_form(
                    bailleur.dg_date_deliberation
                ),
            }
        )
    return {
        **utils.base_convention_response_error(request, convention),
        "form": form,
    }
