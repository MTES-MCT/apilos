from uuid import UUID

import datetime
import logging
from django.db import transaction
from django.http import HttpRequest
from typing import Any

from conventions.forms import AvenantsforavenantForm, InitavenantsforavenantForm
from conventions.forms.avenant import AvenantForm
from conventions.models import AvenantType, Convention, ConventionStatut
from conventions.services import utils
from conventions.services.search import AvenantListSearchService
from upload.services import UploadService

logger = logging.getLogger(__name__)


def create_avenant(request: HttpRequest, convention_uuid: UUID) -> dict[str, Any]:
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

                with transaction.atomic():
                    avenant = convention_to_clone.clone(
                        request.user, convention_origin=parent_convention
                    )

            avenant_type = AvenantType.objects.get(
                nom=avenant_form.cleaned_data["avenant_type"]
            )
            avenant.avenant_types.add(avenant_type)
            avenant.save()  # TODO: check if this is necessary

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


def upload_avenants_for_avenant(
    request: HttpRequest, convention_uuid: UUID
) -> dict[str, Any]:
    parent_convention = (
        Convention.objects.prefetch_related("programme")
        .prefetch_related("lot")
        .prefetch_related("avenants")
        .get(uuid=convention_uuid)
    )
    avenant_search_service = AvenantListSearchService(
        parent_convention, order_by_numero=True
    )

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

    ongoing_avenant_list_service = parent_convention.avenants.all().filter(numero=None)
    return {
        "success": utils.ReturnStatus.ERROR,
        "form": avenant_form,
        "convention": parent_convention,
        "avenants": avenant_search_service.paginate().get_page(
            request.GET.get("page", 1)
        ),
        "ongoing_avenants": ongoing_avenant_list_service,
    }


def _get_last_avenant(convention: Convention) -> Convention:
    avenants_status = {avenant.statut for avenant in convention.avenants.all()}
    if {
        ConventionStatut.PROJET.label,
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    } & avenants_status:
        raise Exception("Ongoing avenant already exists")
    ordered_avenants = convention.avenants.order_by("-cree_le")
    return ordered_avenants[0] if ordered_avenants else convention


def complete_avenants_for_avenant(
    request: HttpRequest, convention_uuid: UUID
) -> dict[str, Any]:
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
            avenant.televersement_convention_signee_le = datetime.date.today()
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
        "avenants_parent": avenant_search_service.paginate().get_page(
            request.GET.get("page", 1)
        ),
        "avenant_form": avenant_form,
        "convention_parent": convention_parent,
    }


def remove_avenant_type_from_avenant(avenant_type: str, convention_uuid: UUID) -> None:
    try:
        avenant_type = AvenantType.objects.get(nom=avenant_type)
    except AvenantType.DoesNotExist:
        logger.error(f"No avenant type named '{avenant_type}'")
        return

    try:
        avenant = Convention.objects.avenants().get(uuid=convention_uuid)
    except Convention.DoesNotExist:
        logger.error(f"No avenant with uuid '{convention_uuid}'")
        return

    if not avenant.avenant_types.filter(pk=avenant_type.pk).exists():
        return

    with transaction.atomic():
        avenant.avenant_types.remove(avenant_type)
