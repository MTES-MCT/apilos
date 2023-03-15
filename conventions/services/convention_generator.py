import datetime
import os
import io
import math
import json
import jinja2
import convertapi

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

from django.conf import settings
from django.forms.models import model_to_dict
from django.template.defaultfilters import date as template_date
from django.core.files.storage import default_storage

from conventions.models import Convention, ConventionType1and2
from conventions.templatetags.custom_filters import (
    get_text_as_list,
    inline_text_multiline,
)
from core.utils import get_key_from_json_field, round_half_up
from programmes.models import (
    Financement,
    Annexe,
    TypologieLogement,
)
from upload.models import UploadedFile
from upload.services import UploadService


class NotHandleConventionType(Exception):
    pass


class ConventionTypeConfigurationError(Exception):
    pass


def get_convention_template_path(convention):
    # pylint: disable=R0911
    if convention.is_avenant():
        if convention.programme.is_foyer() or convention.programme.is_residence():
            return f"{settings.BASE_DIR}/documents/FoyerResidence-Avenant-template.docx"
        return f"{settings.BASE_DIR}/documents/Avenant-template.docx"
    if convention.programme.is_foyer():
        return f"{settings.BASE_DIR}/documents/Foyer-template.docx"
    if convention.programme.is_residence():
        return f"{settings.BASE_DIR}/documents/Residence-template.docx"
    if convention.programme.bailleur.is_hlm():
        return f"{settings.BASE_DIR}/documents/HLM-template.docx"
    if convention.programme.bailleur.is_sem():
        return f"{settings.BASE_DIR}/documents/SEM-template.docx"
    if convention.programme.bailleur.is_type1and2():
        if convention.type1and2 == ConventionType1and2.TYPE1:
            return f"{settings.BASE_DIR}/documents/Type1-template.docx"
        if convention.type1and2 == ConventionType1and2.TYPE2:
            return f"{settings.BASE_DIR}/documents/Type2-template.docx"
    raise ConventionTypeConfigurationError(
        "Le type de convention I ou II doit-être configuré pour les bailleurs"
        + " non SEM ou HLM. Bailleur de type : "
        + convention.programme.bailleur.get_sous_nature_bailleur_display()
    )


def _compute_total_logement(convention):
    logements_totale = {
        "sh_totale": 0,
        "sa_totale": 0,
        "sar_totale": 0,
        "su_totale": 0,
        "loyer_total": 0,
    }
    nb_logements_par_type = {}
    for logement in convention.lot.logements.order_by("typologie").all():
        logements_totale["sh_totale"] += logement.surface_habitable or 0
        logements_totale["sa_totale"] += logement.surface_annexes or 0
        logements_totale["sar_totale"] += logement.surface_annexes_retenue or 0
        logements_totale["su_totale"] += logement.surface_utile or 0
        logements_totale["loyer_total"] += logement.loyer or 0
        if logement.get_typologie_display() not in nb_logements_par_type:
            nb_logements_par_type[logement.get_typologie_display()] = 0
        nb_logements_par_type[logement.get_typologie_display()] += 1
    return (logements_totale, nb_logements_par_type)


def _compute_total_locaux_collectifs(convention):
    return sum(
        locaux_collectif.surface_habitable
        for locaux_collectif in convention.lot.locaux_collectifs.all()
    )


def generate_convention_doc(convention: Convention, save_data=False):
    # pylint: disable=R0912,R0914,R0915
    annexes = (
        Annexe.objects.prefetch_related("logement")
        .filter(logement__lot_id=convention.lot.id)
        .all()
    )

    # It is an avenant
    avenant_data = {}
    if convention.is_avenant():
        for avenant_type in convention.avenant_types.all():
            avenant_data[f"avenant_type_{avenant_type}"] = True

    filepath = get_convention_template_path(convention)
    doc = DocxTemplate(filepath)
    (logements_totale, nb_logements_par_type) = _compute_total_logement(convention)

    logement_edds, lot_num = _prepare_logement_edds(convention)
    # tester si il logement exists avant de commencer

    object_images, local_pathes = _get_object_images(doc, convention)

    context = {
        **avenant_data,
        "convention": convention,
        "bailleur": convention.programme.bailleur,
        "programme": convention.programme,
        "lot": convention.lot,
        "administration": convention.programme.administration,
        "logement_edds": logement_edds,
        "logements": convention.lot.logements.order_by("typologie").all(),
        "locaux_collectifs": convention.lot.locaux_collectifs.all(),
        "annexes": annexes,
        "stationnements": convention.lot.type_stationnements.all(),
        "prets_cdc": convention.prets.filter(preteur__in=["CDCF", "CDCL"]),
        "autres_prets": convention.prets.exclude(preteur__in=["CDCF", "CDCL"]),
        "references_cadastrales": convention.programme.referencecadastrales.all(),
        "nb_logements_par_type": nb_logements_par_type,
        "lot_num": lot_num,
        "loyer_m2": _get_loyer_par_metre_carre(convention),
        "liste_des_annexes": _compute_liste_des_annexes(
            convention.lot.type_stationnements.all(), annexes
        ),
        "lc_sh_totale": _compute_total_locaux_collectifs(convention),
        "nombre_annees_conventionnement": (
            convention.date_fin_conventionnement.year - datetime.date.today().year
            if convention.date_fin_conventionnement
            else "---"
        ),
    }
    context.update(_compute_mixte(convention))
    context.update(logements_totale)
    context.update(object_images)

    doc.render(context, _get_jinja_env())
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    for local_path in list(set(local_pathes)):
        os.remove(local_path)

    if save_data:
        _save_convention_donnees_validees(
            convention,
            logement_edds,
            nb_logements_par_type,
            lot_num,
            logements_totale,
        )

    return file_stream


def typologie_label(typologie: str):
    typo = (
        TypologieLogement(typologie).label
        if typologie in TypologieLogement
        else typologie
    )
    return (
        typo.replace("T", "Logement T ") if typo in TypologieLogement.labels else None
    )


def default_str_if_none(text_field):
    return text_field if text_field else "---"


def default_empty_if_none(text_field):
    return text_field if text_field else ""


def to_fr_date(date):
    """
    Display french date using the date function from django.template.defaultfilters
    Write the date in number (ex : 05/01/2021). More about format syntax here :
    https://docs.djangoproject.com/fr/4.0/ref/templates/builtins/#date
    """
    return template_date(date, "j F Y") if date else ""


def to_fr_date_or_default(date):
    return template_date(date, "j F Y") if date else "---"


def to_fr_short_date(date):
    return template_date(date, "d/m/Y") if date else ""


def to_fr_short_date_or_default(date):
    return template_date(date, "d/m/Y") if date else "---"


def _get_jinja_env():
    jinja_env = jinja2.Environment(autoescape=True)
    jinja_env.filters["d"] = to_fr_date
    jinja_env.filters["dd"] = to_fr_date_or_default
    jinja_env.filters["sd"] = to_fr_short_date
    jinja_env.filters["sdd"] = to_fr_short_date_or_default
    jinja_env.filters["f"] = _to_fr_float
    jinja_env.filters["pl"] = pluralize
    jinja_env.filters["len"] = len
    jinja_env.filters["inline_text_multiline"] = inline_text_multiline
    jinja_env.filters["get_text_as_list"] = get_text_as_list
    jinja_env.filters["default_str_if_none"] = default_str_if_none
    jinja_env.filters["default_empty_if_none"] = default_empty_if_none
    jinja_env.filters["tl"] = typologie_label

    return jinja_env


def _save_convention_donnees_validees(
    convention,
    logement_edds,
    nb_logements_par_type,
    lot_num,
    logements_totale,
):

    annexes = (
        Annexe.objects.prefetch_related("logement")
        .filter(logement__lot_id=convention.lot.id)
        .all()
    )

    context_to_save = {
        "convention": model_to_dict(convention),
        "bailleur": model_to_dict(convention.programme.bailleur),
        "programme": model_to_dict(convention.programme),
        "lot": model_to_dict(convention.lot),
        "administration": model_to_dict(convention.programme.administration),
        "logement_edds": _list_to_dict(logement_edds),
        "logements": _list_to_dict(convention.lot.logements.all()),
        "annexes": _list_to_dict(annexes),
        "stationnements": _list_to_dict(convention.lot.type_stationnements.all()),
        "prets_cdc": _list_to_dict(
            convention.prets.filter(preteur__in=["CDCF", "CDCL"])
        ),
        "autres_prets": _list_to_dict(
            convention.prets.exclude(preteur__in=["CDCF", "CDCL"])
        ),
        "references_cadastrales": _list_to_dict(
            convention.programme.referencecadastrales.all()
        ),
        "nb_logements_par_type": nb_logements_par_type,
        "lot_num": lot_num,
        "loyer_m2": _get_loyer_par_metre_carre(convention),
        "liste_des_annexes": _compute_liste_des_annexes(
            convention.lot.type_stationnements.all(), annexes
        ),
    }
    context_to_save.update(_compute_mixte(convention))
    context_to_save.update(logements_totale)
    object_files = {}
    object_files["vendeur_files"] = convention.programme.vendeur_files()
    object_files["acquereur_files"] = convention.programme.acquereur_files()
    object_files[
        "reference_notaire_files"
    ] = convention.programme.reference_notaire_files()
    object_files[
        "reference_publication_acte_files"
    ] = convention.programme.reference_publication_acte_files()
    object_files[
        "reference_cadastrale_files"
    ] = convention.programme.reference_cadastrale_files()
    object_files["effet_relatif_files"] = convention.programme.effet_relatif_files()
    object_files["edd_volumetrique_files"] = convention.lot.edd_volumetrique_files()
    object_files["edd_classique_files"] = convention.lot.edd_classique_files()
    convention.donnees_validees = json.dumps(
        {**context_to_save, **object_files}, default=str
    )
    convention.save()


def generate_pdf(file_stream: io.BytesIO, convention: Convention):
    # save the convention docx locally
    local_docx_path = str(settings.MEDIA_ROOT) + f"/convention_{convention.uuid}.docx"

    # get a pdf version
    if settings.CONVERTAPI_SECRET:
        with open(local_docx_path, "wb") as local_file:
            local_file.write(file_stream.read())
            local_file.close()

        convertapi.api_secret = settings.CONVERTAPI_SECRET
        result = convertapi.convert("pdf", {"File": local_docx_path})

        convention_dirpath = f"conventions/{convention.uuid}/convention_docs"
        convention_filename = f"{convention.uuid}.pdf"
        pdf_path = _save_io_as_file(
            result.file.io, convention_dirpath, convention_filename
        )

        # remove docx version
        os.remove(local_docx_path)
    else:
        convention_dirpath = f"conventions/{convention.uuid}/convention_docs"
        convention_filename = f"{convention.uuid}.docx"
        pdf_path = _save_io_as_file(
            file_stream, convention_dirpath, convention_filename
        )

    file_stream.seek(0)

    # END PDF GENERATION
    return pdf_path


def _save_io_as_file(file_io, convention_dirpath, convention_filename):

    upload_service = UploadService(
        convention_dirpath=convention_dirpath, filename=convention_filename
    )
    upload_service.upload_file_io(file_io)
    return f"{convention_dirpath}/{convention_filename}"


def _to_fr_float(value, d=2):
    if value is None:
        return ""
    return format(value, f",.{d}f").replace(",", " ").replace(".", ",")


def pluralize(value):
    if value is not None and value > 1:
        return "s"
    return ""


def _build_files_for_docx(doc, convention_uuid, file_list):
    # pylint: disable=R1732
    local_pathes = []
    docx_images = []
    files = UploadedFile.objects.filter(uuid__in=file_list)
    for object_file in files:
        if "image" in object_file.content_type:
            with default_storage.open(
                object_file.filepath(convention_uuid),
                "rb",
            ) as file:
                local_path = (
                    settings.MEDIA_ROOT / f"{object_file.uuid}_{object_file.filename}"
                )
                local_file = open(local_path, "wb")
                local_file.write(file.read())
                local_file.close()
            docx_images.append(
                InlineImage(doc, image_descriptor=f"{local_path}", width=Inches(5))
            )
            local_pathes.append(f"{local_path}")
    return docx_images, local_pathes


def get_files_attached(convention):
    local_pathes = []
    attached_files = get_key_from_json_field(convention.attached, "files", default={})

    files = UploadedFile.objects.filter(uuid__in=attached_files)
    for object_file in files:
        file = UploadService().get_file(object_file.filepath(convention.uuid))
        local_path = (
            settings.MEDIA_ROOT
            / "conventions"
            / str(convention.uuid)
            / "attached_files"
            / object_file.filename
        )
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as local_file:
            local_file.write(file.read())
            file.close()
        local_pathes.append(local_path)
    return local_pathes


def _get_object_images(doc, convention):
    object_images = {}
    local_pathes = []
    vendeur_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.vendeur_files()
    )
    object_images["vendeur_images"] = vendeur_images
    local_pathes += tmp_local_path
    acquereur_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.acquereur_files()
    )
    object_images["acquereur_images"] = acquereur_images
    local_pathes += tmp_local_path
    reference_notaire_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.reference_notaire_files()
    )
    object_images["reference_notaire_images"] = reference_notaire_images
    local_pathes += tmp_local_path
    reference_publication_acte_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.reference_publication_acte_files()
    )
    object_images[
        "reference_publication_acte_images"
    ] = reference_publication_acte_images
    local_pathes += tmp_local_path
    reference_cadastrale_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.reference_cadastrale_files()
    )
    object_images["reference_cadastrale_images"] = reference_cadastrale_images
    local_pathes += tmp_local_path
    effet_relatif_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.effet_relatif_files()
    )
    object_images["effet_relatif_images"] = effet_relatif_images
    local_pathes += tmp_local_path
    edd_volumetrique_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.lot.edd_volumetrique_files()
    )
    object_images["edd_volumetrique_images"] = edd_volumetrique_images
    local_pathes += tmp_local_path
    edd_classique_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.lot.edd_classique_files()
    )
    object_images["edd_classique_images"] = edd_classique_images
    local_pathes += tmp_local_path

    return object_images, local_pathes


def _get_loyer_par_metre_carre(convention):
    logement = convention.lot.logements.first()
    if logement:
        return convention.lot.logements.first().loyer_par_metre_carre
    return 0


def _compute_liste_des_annexes(typestationnements, annexes):
    annexes_par_type = {}
    for annexe in annexes:
        if annexe.get_typologie_display() not in annexes_par_type:
            annexes_par_type[annexe.get_typologie_display()] = 0
        annexes_par_type[annexe.get_typologie_display()] += 1

    stationnement_par_type = {}
    for stationnement in typestationnements:
        if stationnement.get_typologie_display() not in stationnement_par_type:
            stationnement_par_type[stationnement.get_typologie_display()] = 0
        stationnement_par_type[
            stationnement.get_typologie_display()
        ] += stationnement.nb_stationnements

    annexes_list = []
    for key, value in annexes_par_type.items():
        annexes_list.append(
            f"{value} annexe{'s' if value > 1 else ''} de type {key.lower()}"
        )
    for key, value in stationnement_par_type.items():
        annexes_list.append(
            f"{value} stationnement{'s' if value > 1 else ''} de type {key.lower()}"
        )

    return ", ".join(annexes_list)


def _compute_mixte(convention):
    mixite = {
        "mixPLUSsup10_30pc": 0,
        "mixPLUSinf10_30pc": 0,
        "mixPLUSinf10_10pc": 0,
        "mixPLUS_30pc": 0,
        "mixPLUS_10pc": 0,
    }
    if convention.lot.financement == Financement.PLUS:
        mixite["mixPLUS_10pc"] = round_half_up(convention.lot.nb_logements * 0.1)
        # cf. convention : 30 % au moins des logements
        if convention.lot.nb_logements < 10:
            # cf. convention : 30 % au moins des logements (ce nombre s'obtenant en arrondissant
            # à l'unité la plus proche le résultat de l'application du pourcentage)
            mixite["mixPLUS_30pc"] = round_half_up(convention.lot.nb_logements * 0.3)
            mixite["mixPLUSinf10_30pc"] = round_half_up(
                convention.lot.nb_logements * 0.3
            )
            # cf. convention : 10 % des logements
            mixite["mixPLUSinf10_10pc"] = round_half_up(
                convention.lot.nb_logements * 0.1
            )
        else:
            # cf. convention : 30 % au moins des logements
            mixite["mixPLUSsup10_30pc"] = math.ceil(convention.lot.nb_logements * 0.3)
            mixite["mixPLUS_30pc"] = math.ceil(convention.lot.nb_logements * 0.3)

    return mixite


def _prepare_logement_edds(convention):
    logement_edds = convention.programme.logementedds.order_by(
        "financement", "designation"
    ).all()
    count = 0
    financement = None
    lot_num = 0
    for logement_edd in logement_edds:
        if financement != logement_edd.financement:
            financement = logement_edd.financement
            count = count + 1
            if convention.lot.financement == logement_edd.financement:
                lot_num = count
        logement_edd.lot_num = count
    return logement_edds, lot_num


def _list_to_dict(object_list):
    return list(map(model_to_dict, object_list))


def fiche_caf_doc(convention):
    filepath = f"{settings.BASE_DIR}/documents/FicheCAF-template.docx"

    doc = DocxTemplate(filepath)

    logements_totale = {
        "sh_totale": 0,
        "sa_totale": 0,
        "sar_totale": 0,
        "su_totale": 0,
        "loyer_total": 0,
    }
    nb_logements_par_type = {}
    for logement in convention.lot.logements.order_by("typologie").all():
        logements_totale["sh_totale"] += logement.surface_habitable or 0
        logements_totale["sa_totale"] += logement.surface_annexes or 0
        logements_totale["sar_totale"] += logement.surface_annexes_retenue or 0
        logements_totale["su_totale"] += logement.surface_utile or 0
        logements_totale["loyer_total"] += logement.loyer or 0
        if logement.get_typologie_display() not in nb_logements_par_type:
            nb_logements_par_type[logement.get_typologie_display()] = 0
        nb_logements_par_type[logement.get_typologie_display()] += 1

    lot_num = _prepare_logement_edds(convention)
    # tester si le logement existe avant de commencer

    context = {
        "convention": convention,
        "bailleur": convention.programme.bailleur,
        "programme": convention.programme,
        "lot": convention.lot,
        "administration": convention.programme.administration,
        "logements": convention.lot.logements.all(),
        "nb_logements_par_type": nb_logements_par_type,
        "lot_num": lot_num,
        "loyer_m2": _get_loyer_par_metre_carre(convention),
    }
    context.update(logements_totale)

    doc.render(context, _get_jinja_env())
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    return file_stream
