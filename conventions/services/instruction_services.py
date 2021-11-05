import datetime

from programmes.models import (
    Annexe,
)
from conventions.models import Convention, ConventionStatut
from . import utils
from . import convention_generator


def convention_summary(request, convention_uuid):
    convention = (
        Convention.objects.prefetch_related("bailleur")
        .prefetch_related("programme")
        .prefetch_related("programme__referencecadastrale_set")
        .prefetch_related("programme__logementedd_set")
        .prefetch_related("lot")
        .prefetch_related("lot__typestationnement_set")
        .prefetch_related("lot__logement_set")
        .get(uuid=convention_uuid)
    )
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
        "bailleur": convention.bailleur,
        "lot": convention.lot,
        "programme": convention.programme,
        "logement_edds": convention.programme.logementedd_set.all(),
        "logements": convention.lot.logement_set.all(),
        "stationnements": convention.lot.typestationnement_set.all(),
        "reference_cadastrales": convention.programme.referencecadastrale_set.all(),
        "annexes": Annexe.objects.filter(logement__lot_id=convention.lot.id).all(),
        "editable": request.user.has_perm("convention.change_convention", convention),
    }


def convention_save(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    submitted = utils.ReturnStatus.WARNING
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if request.POST.get("SubmitConvention", False):
            if convention.premiere_soumission_le is None:
                convention.premiere_soumission_le = datetime.datetime.now()
            convention.soumis_le = datetime.datetime.now()
            convention.statut = ConventionStatut.INSTRUCTION
            convention.save()
            submitted = utils.ReturnStatus.SUCCESS
        return {
            "success": submitted,
            "convention": convention,
        }
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
    }


def convention_validate(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    if request.method == "POST":
        request.user.check_perm("convention.change_convention", convention)
        if not convention.valide_le:
            convention.valide_le = datetime.datetime.now()
        convention.statut = ConventionStatut.VALIDE
        convention.save()
        submitted = utils.ReturnStatus.SUCCESS
        return {
            "success": submitted,
            "convention": convention,
        }
    return {
        "success": utils.ReturnStatus.ERROR,
        "convention": convention,
    }


def generate_convention(convention_uuid):
    convention = (
        Convention.objects.prefetch_related("bailleur")
        .prefetch_related("lot")
        .prefetch_related("lot__typestationnement_set")
        .prefetch_related("lot__logement_set")
        .prefetch_related("pret_set")
        .prefetch_related("programme")
        .prefetch_related("programme__administration")
        .prefetch_related("programme__logementedd_set")
        .prefetch_related("programme__referencecadastrale_set")
        .get(uuid=convention_uuid)
    )
    file_stream = convention_generator.generate_hlm(convention)
    return file_stream, f"{convention}"
