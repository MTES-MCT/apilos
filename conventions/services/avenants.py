import datetime

from django.utils import timezone

from conventions.forms import (
    InitavenantsforavenantForm,
    AvenantsforavenantForm,
    ConventionResiliationForm,
    UploadForm,
    ConventionDateForm,
)
from conventions.forms.avenant import AvenantForm
from conventions.models import (
    AvenantType,
    Convention,
    ConventionStatut,
)
from conventions.services import utils
from conventions.services.search import AvenantListSearchService
from upload.services import UploadService


def create_avenant(request, convention_uuid):
    parent_convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .prefetch_related("avenants")
        .get(uuid=convention_uuid)
    )
    if parent_convention.is_avenant():
        parent_convention = (
            Convention.objects.prefetch_related("programme")
            .prefetch_related("lot")
            .prefetch_related("avenants")
            .get(id=parent_convention.parent_id)
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


def upload_avenants_for_avenant(request, convention_uuid):
    parent_convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .prefetch_related("avenants")
        .get(uuid=convention_uuid)
    )
    avenant_search_service = AvenantListSearchService(
        parent_convention, order_by_numero=True
    )

    ongoing_avenant_list_service = parent_convention.avenants.all().filter(numero=None)
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
        "avenants": avenant_search_service.get_results(),
        "ongoing_avenants": ongoing_avenant_list_service,
    }


def convention_post_action(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    result_status = None
    form_posted = None
    if request.method == "POST":
        resiliation_form = ConventionResiliationForm(request.POST)
        updatedate_form = ConventionDateForm(request.POST)
        is_resiliation = request.POST.get("resiliation", False)
        if is_resiliation:
            if resiliation_form.is_valid():
                convention.statut = ConventionStatut.RESILIEE.label
                convention.date_resiliation = resiliation_form.cleaned_data[
                    "date_resiliation"
                ]
                convention.save()
                # SUCCESS
                result_status = utils.ReturnStatus.SUCCESS
                form_posted = "resiliation"
        else:
            if updatedate_form.is_valid():
                convention.televersement_convention_signee_le = (
                    updatedate_form.cleaned_data["televersement_convention_signee_le"]
                )
                convention.save()
                result_status = utils.ReturnStatus.SUCCESS
                form_posted = "date_signature"

    else:
        resiliation_form = ConventionResiliationForm()
        updatedate_form = ConventionDateForm()

    upform = UploadForm()
    avenant_search_service = AvenantListSearchService(convention, order_by_numero=True)

    total_avenants = convention.avenants.all().count()

    return {
        "success": result_status,
        "upform": upform,
        "convention": convention,
        "avenants": avenant_search_service.get_results(),
        "total_avenants": total_avenants,
        "resiliation_form": resiliation_form,
        "updatedate_form": updatedate_form,
        "form_posted": form_posted,
    }


def _get_last_avenant(convention):
    avenants_status = {avenant.statut for avenant in convention.avenants.all()}
    if {
        ConventionStatut.PROJET.label,
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    } & avenants_status:
        raise Exception("Ongoing avenant already exists")
    ordered_avenants = convention.avenants.order_by("-cree_le")
    return ordered_avenants[0] if ordered_avenants else convention


def complete_avenants_for_avenant(request, convention_uuid):
    avenant = Convention.objects.get(uuid=convention_uuid)
    convention_parent = avenant.parent
    avenant_search_service = AvenantListSearchService(
        avenant.parent, order_by_numero=True
    )

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
            avenant.statut = ConventionStatut.SIGNEE.label
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
        "avenants_parent": avenant_search_service.get_results(),
        "avenant_form": avenant_form,
        "convention_parent": convention_parent,
    }
