import json
import logging
from datetime import datetime
from enum import Enum

import openpyxl
from django.http import HttpRequest
from openpyxl.styles import Font

from conventions.models import Convention, ConventionStatut
from conventions.templatetags.custom_filters import is_bailleur, is_instructeur
from core.utils import is_valid_uuid
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from upload.models import UploadedFile

logger = logging.getLogger(__name__)


def format_date_for_form(date):
    return date.strftime("%Y-%m-%d") if date is not None else ""


class ReturnStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    # used to manage success without redirect on next step on step form
    REFRESH = "REFRESH"


def set_files_and_text_field(files_field, text_field=""):
    files = []
    if files_field and files_field != "None" and isinstance(files_field, str):
        files = json.loads(files_field)
    field = {"files": files, "text": text_field}
    return json.dumps(field)


def get_text_and_files_from_field(name, field):
    object_field = {}

    files = {}
    if field:
        try:
            object_field = json.loads(field)
            # Fix potentially malformed JSON
            if not isinstance(object_field["files"], dict):
                object_field["files"] = {}
        except json.decoder.JSONDecodeError:
            object_field = {
                "files": {},
                "text": field if isinstance(field, str) else "",
            }
        files = {
            k: v
            for k, v in object_field.get("files", files).items()
            if is_valid_uuid(k)
        }
    returned_files = {}
    for file in UploadedFile.objects.filter(uuid__in=files):
        returned_files[str(file.uuid)] = {
            "uuid": str(file.uuid),
            "filename": file.filename,
            "realname": file.realname,
            "size": file.size,
            "content_type": file.content_type,
            "thumbnail": (
                files[str(file.uuid)]["thumbnail"]
                if "thumbnail" in files[str(file.uuid)]
                else None
            ),
        }
    object_field["files"] = json.dumps(returned_files)
    return {
        name: object_field["text"] if "text" in object_field else "",
        name + "_files": object_field["files"],
    }


def init_text_and_files_from_field(request, object_instance, field_name):
    if (
        request.POST.get(field_name + "_files") is not None
        or request.POST.get(field_name) is not None
    ):
        form_fields = {}
        form_fields[field_name] = request.POST.get(field_name)
        form_fields[field_name + "_files"] = request.POST.get(field_name + "_files")
        return form_fields
    return get_text_and_files_from_field(
        field_name, getattr(object_instance, field_name)
    )


def get_form_value(form_instance, object_instance, field_name):
    if form_instance[field_name].value() is not None:
        return form_instance[field_name].value()
    return getattr(object_instance, field_name)


def get_form_date_value(form_instance, object_instance, field_name):
    if form_instance[field_name].value() is not None:
        return form_instance[field_name].value()
    return format_date_for_form(
        getattr(object_instance, field_name)
    )  # format_date_for_form(


def build_partial_form(
    request, convention_object, field_list, non_attribute_field_list=None
):
    fields_dict = {}
    if non_attribute_field_list is None:
        non_attribute_field_list = []
    for field in field_list:
        fields_dict[field] = request.POST.get(field, getattr(convention_object, field))
    for non_attribute_field in non_attribute_field_list:
        fields_dict[non_attribute_field] = request.POST.get(non_attribute_field)
    return fields_dict


def build_partial_text_and_files_form(request, convention_object, field_list):
    fields_dict = {}
    for field in field_list:
        fields_dict = {
            **fields_dict,
            **init_text_and_files_from_field(request, convention_object, field),
        }
    return fields_dict


def base_convention_response_error(request, convention):
    return {
        "success": ReturnStatus.ERROR,
        "convention": convention,
        "comments": convention.get_comments_dict(),
        "editable": editable_convention(request, convention),
    }


def editable_convention(request: HttpRequest, convention: Convention):
    if "readonly" in request.session and request.session["readonly"]:
        return False
    if is_instructeur(request):
        if "is_expert" in request.session and request.session["is_expert"] is True:
            return True
        return convention.statut in [
            ConventionStatut.PROJET.label,
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
        ]
    if is_bailleur(request):
        return convention.statut == ConventionStatut.PROJET.label
    return False


def set_from_form_or_object(field, form, obj):
    setattr(
        obj,
        field,
        (
            form.cleaned_data[field]
            if form.cleaned_data[field] is not None
            else getattr(obj, field)
        ),
    )


def convention_upload_filename(convention: Convention) -> str:

    def _normalize(numero: str | None) -> str | None:
        if numero:
            return numero.replace(" ", "_")

    parts = []

    if convention.parent:
        parts += [
            f"convention_{_normalize(convention.parent.numero)}",
            f"avenant_{_normalize(convention.numero) or 'N'}",
        ]
    else:
        parts += [
            f"convention_{_normalize(convention.numero) or 'NUM'}",
        ]

    if convention.statut == ConventionStatut.PROJET.label:
        parts.append("projet")

    parts.append(datetime.now().strftime("%Y-%m-%d_%H-%M"))

    return f"{'_'.join(parts)}.pdf"


def _can_delete_action_alerte(alerte, destinataire):
    if destinataire == "MO":
        return any(
            dest["codeProfil"] == "MO_PERS_MORALE" for dest in alerte["destinataires"]
        )

    if destinataire == "SG":
        return any(dest["codeProfil"] == "SER_GEST" for dest in alerte["destinataires"])

    return destinataire is None


def delete_action_alertes(convention, siap_credentials, destinataire=None):
    """
    Delete all action alertes related to the convention
    """
    client = SIAPClient.get_instance()
    alertes = client.list_convention_alertes(
        convention_id=convention.uuid, **siap_credentials
    )
    for alerte in alertes:

        if alerte["categorie"] != "CATEGORIE_ALERTE_ACTION":
            continue

        can_delete = _can_delete_action_alerte(alerte, destinataire)

        if can_delete:
            try:
                client.delete_alerte(
                    user_login=siap_credentials["user_login"],
                    habilitation_id=siap_credentials["habilitation_id"],
                    alerte_id=alerte["id"],
                )
            except SIAPException as e:
                logger.warning(e)
CONVENTION_EXPORT_MAX_ROWS = 5000


def get_convention_export_excel_header(request):
    headers = [
        "Année de gestion",
        "Numéro d'opération SIAP",
        "Numéro de convention",
        "Commune",
        "Code postal",
        "Nom de l'opération",
        "Instructeur" if request.user.is_instructeur else "Bailleur",
        "Type de financement",
        "Nombre de logements",
        "Nature de l'opération",
        "Date de signature",
        "Montant du loyer au m2",
        "Livraison",
    ]

    return headers


def get_convention_export_excel_row(request, convention):
    row = []
    # 1. Année de gestion
    row.append(
        convention.programme.annee_gestion_programmation if convention.programme else ""
    )
    # 2. Numéro d'opération SIAP
    row.append(convention.programme.numero_operation if convention.programme else "")
    # 3. Numéro de convention
    if convention.numero and not convention.parent:
        row.append(convention.numero)
    elif convention.parent:
        row.append(convention.parent.numero)
    else:
        row.append("")
    # 4. Si avenant : numéro
    # 5. Commune
    row.append(convention.programme.ville if convention.programme else "")
    # 6. Code postal
    row.append(convention.programme.code_postal if convention.programme else "")
    # 7. Nom de l'opération
    row.append(convention.programme.nom if convention.programme else "")
    # 8. Bailleur OR instructeur
    if request.user.is_instructeur:
        row.append(
            convention.programme.administration.nom
            if convention.programme.administration
            else ""
        )
    else:
        row.append(
            convention.programme.bailleur.nom if convention.programme.bailleur else ""
        )
    # 9. Type de financement
    row.append(convention.lot.get_financement_display())
    # 10. Nombre de logements
    row.append(convention.lot.nb_logements)
    # 11. Nature de l'opération dans programe
    row.append(convention.programme.nature_logement if convention.programme else "")
    # 12. Date de signature
    signature = convention.televersement_convention_signee_le
    formatted_signature_date = signature.strftime("%d/%m/%Y") if signature else "-"
    row.append(formatted_signature_date)
    # 13. Montant du loyer au m2
    logement = convention.lot.logements.first()
    row.append(logement.loyer_par_metre_carre if logement else 0)
    # 14. Livraison
    livraison = convention.programme.date_achevement_compile
    row.append(livraison.strftime("%d/%m/%Y") if livraison else "-")

    return row


def create_convention_export_excel(request, conventions, filters=None):
    import logging

    logging.warning("Fetched %d conventions", conventions.count())
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Conventions"
    ws.append(get_convention_export_excel_header(request))

    for cell in ws[1]:
        cell.font = Font(bold=True)
    for convention in conventions[:CONVENTION_EXPORT_MAX_ROWS]:
        ws.append(get_convention_export_excel_row(request, convention))

    return wb
