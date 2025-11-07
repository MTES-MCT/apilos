import json
from datetime import date, datetime
from enum import Enum

import openpyxl
from django.http import HttpRequest
from openpyxl.styles import Font

from conventions.models import Convention, ConventionStatut
from conventions.templatetags.custom_filters import is_bailleur, is_instructeur
from core.utils import is_valid_uuid
from upload.models import UploadedFile

CONVENTION_EXPORT_MAX_ROWS = 5000


class FileType(Enum):
    CONVENTION = "Convention"
    PUBLICATION = "Publication"


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


def convention_upload_filename(
    convention: Convention, as_type: FileType = FileType.CONVENTION
) -> str:

    def _normalize(numero: str | None) -> str | None:
        if numero:
            new_numero_syntax = numero.replace(" ", "_")
            if as_type == FileType.PUBLICATION:
                return new_numero_syntax.replace("/", "_")
            return new_numero_syntax

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

    base_filename = f"{'_'.join(parts)}.pdf"

    if as_type == FileType.PUBLICATION:
        return f"publication_{base_filename}"

    return base_filename


def stringify_date(date_value, format="%d/%m/%Y"):
    """
    Convertit les dates en chaînes de caractères formatées.
    """
    if date_value and isinstance(date_value, date):
        return date_value.strftime(format)
    return "-"


def get_convention_export_excel_header(request):
    headers = [
        "Numéro d'opération SIAP",
        "Numéro de convention",
        "Numéro d'avenant",
        "Statut de la convention",
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
        "Date de fin de conventionnement",
    ]

    return headers


def get_convention_export_excel_row(request, convention):
    return [
        convention.programme.numero_operation,  # 1. Numéro d'opération SIAP
        (
            convention.numero
            if convention.numero and not convention.parent
            else (convention.parent.numero if convention.parent else "")
        ),  # 1. Numéro de convention
        convention.numero if convention.parent else "",  # 3. Numéro d'avenant
        convention.statut,  # 4. statut de la convention
        convention.programme.ville,  # 5. Commune
        convention.programme.code_postal,  # 6. Code postal
        convention.programme.nom,  # 7. Nom de l'opération
        (
            convention.programme.administration.nom
            if request.user.is_instructeur
            else convention.programme.bailleur.nom
        ),  # 8. Instructeur or Bailleur
        convention.lot.get_financement_display(),  # 9. Type de financement
        convention.lot.nb_logements,  # 10. Nombre de logements
        convention.programme.nature_logement,  # 11. Nature de l'opération dans programme
        stringify_date(
            convention.televersement_convention_signee_le
        ),  # 12. Date de signature
        (
            convention.lot.logements.first().loyer_par_metre_carre
            if convention.lot.logements.first()
            else ""
        ),  # 13. Montant du loyer au m2
        stringify_date(convention.programme.date_achevement_compile),  # 14. Livraison
        stringify_date(
            convention.date_fin_conventionnement
        ),  # 15. Date de fin de conventionnement
    ]


def create_convention_export_excel(request, conventions, filters=None):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Conventions"
    ws.append(get_convention_export_excel_header(request))

    for cell in ws[1]:
        cell.font = Font(bold=True)
    for convention in conventions[:CONVENTION_EXPORT_MAX_ROWS]:
        ws.append(get_convention_export_excel_row(request, convention))

    return wb
