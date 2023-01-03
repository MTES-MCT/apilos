import datetime

from django.utils import timezone

from conventions.forms import (
    InitavenantsforavenantForm,
    AvenantsforavenantForm,
)
from conventions.forms.avenant import AvenantForm
from conventions.models import (
    AvenantType,
    Convention,
    ConventionStatut,
)
from conventions.services import utils
from conventions.services.conventions import ConventionListService
from upload.services import UploadService


def create_avenant(request, convention_uuid):
    parent_convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .prefetch_related("avenants")
        .get(uuid=convention_uuid)
    )
    if request.method == "POST":
        avenant_form = AvenantForm(request.POST)
        if avenant_form.is_valid():
            if avenant_form.cleaned_data["uuid"]:
                avenant = Convention.objects.get(uuid=avenant_form.cleaned_data["uuid"])
            else:
                convention_to_clone = _get_last_avenant(parent_convention)
                avenant = convention_to_clone.clone(
                    request.user, convention_origin=parent_convention
                )
            avenant_type = AvenantType.objects.get(
                nom=avenant_form.cleaned_data["avenant_type"]
            )
            avenant.avenant_types.add(avenant_type)
            avenant.save()
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": avenant,
                "parent_convention": parent_convention,
                "avenant_type": avenant_type,
            }
    else:
        avenant_form = AvenantForm()

    return {
        "success": utils.ReturnStatus.ERROR,
        "editable": request.user.has_perm("convention.add_convention"),
        "bailleurs": request.user.bailleurs(),
        "form": avenant_form,
        "parent_convention": parent_convention,
    }


def search_result(request):
    departement = request.GET.get("departement", None)
    annee = request.GET.get("annee", None)
    num = request.GET.get("num", None)
    conventions = []
    if departement and annee and num:
        conventions = request.user.conventions().filter(
            programme__code_postal__startswith=departement,
            valide_le__year=annee,
            numero__endswith=num,
        )
    return {"conventions": conventions}


def upload_avenants_for_avenant(request, convention_uuid):
    parent_convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .prefetch_related("avenants")
        .get(uuid=convention_uuid)
    )
    avenant_list_service = ConventionListService(
        my_convention_list=parent_convention.avenants.all()
        .prefetch_related("programme")
        .prefetch_related("lot"),
        order_by="cree_le",
    )
    ongoing_avenant_list_service = parent_convention.avenants.all().filter(numero=None)
    avenant_list_service.paginate()
    if request.method == "POST":
        avenant_form = InitavenantsforavenantForm(request.POST)
        if avenant_form.is_valid():
            convention_to_clone = _get_last_avenant(parent_convention)
            avenant = convention_to_clone.clone(
                request.user, convention_origin=parent_convention
            )
            avenant.save()
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "convention": avenant,
                "parent_convention": parent_convention,
            }
    else:
        avenant_form = InitavenantsforavenantForm()
    return {
        "success": utils.ReturnStatus.ERROR,
        "form": avenant_form,
        "convention": parent_convention,
        "avenants": avenant_list_service,
        "ongoing_avenants": ongoing_avenant_list_service,
    }


def _get_last_avenant(convention):
    avenants_status = {avenant.statut for avenant in convention.avenants.all()}
    if {
        ConventionStatut.PROJET,
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
    } & avenants_status:
        raise Exception("Ongoing avenant already exists")
    ordered_avenants = convention.avenants.order_by("-cree_le")
    return ordered_avenants[0] if ordered_avenants else convention


def complete_avenants_for_avenant(request, convention_uuid):
    avenant = Convention.objects.get(uuid=convention_uuid)
    convention_parent = avenant.parent
    avenant_list_service = ConventionListService(
        my_convention_list=avenant.parent.avenants.all()
        .prefetch_related("programme")
        .prefetch_related("lot"),
        order_by="numero",
    )
    avenant_list_service.paginate()
    avenant_numero = avenant.get_default_convention_number()
    if request.method == "POST":
        avenant_form = AvenantsforavenantForm(request.POST, request.FILES)
        if avenant_form.is_valid():
            file = request.FILES["nom_fichier_signe"]
            if file:
                now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                filename = f"{now}_convention_{avenant.uuid}_signed.pdf"
                upload_service = UploadService(
                    convention_dirpath=f"conventions/{avenant.uuid}/convention_docs",
                    filename=filename,
                )
                upload_service.upload_file(file)
                avenant.nom_fichier_signe = filename
            for avenant_type in avenant_form.cleaned_data["avenant_types"]:
                avenanttype = AvenantType.objects.get(nom=avenant_type)
                avenant.avenant_types.add(avenanttype)
            avenant.televersement_convention_signee_le = timezone.now()
            avenant.statut = ConventionStatut.SIGNEE
            avenant.numero = avenant.get_default_convention_number()
            avenant.desc_avenant = avenant_form.cleaned_data["desc_avenant"]
            avenant.save()
            return {
                "success": utils.ReturnStatus.SUCCESS,
                "avenant_form": avenant_form,
                "avenant": avenant,
                "convention_parent": convention_parent,
            }
    else:
        avenant_form = AvenantsforavenantForm()
    return {
        "success": utils.ReturnStatus.ERROR,
        "avenant_numero": avenant_numero,
        "avenants_parent": avenant_list_service,
        "avenant_form": avenant_form,
        "convention_parent": convention_parent,
    }
