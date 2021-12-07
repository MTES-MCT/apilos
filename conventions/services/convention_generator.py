import os
import errno
import io
import jinja2
import convertapi

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

from django.conf import settings
from django.core.files.storage import default_storage

from programmes.models import (
    Financement,
    Annexe,
)
from upload.models import UploadedFile


def generate_hlm(convention):
    # pylint: disable=R0914
    annexes = (
        Annexe.objects.prefetch_related("logement")
        .filter(logement__lot_id=convention.lot.id)
        .all()
    )
    filepath = f"{settings.BASE_DIR}/documents/HLM-template.docx"
    doc = DocxTemplate(filepath)

    logements_totale = {
        "sh_totale": 0,
        "sa_totale": 0,
        "sar_totale": 0,
        "su_totale": 0,
        "loyer_total": 0,
    }
    nb_logements_par_type = {}
    for logement in convention.lot.logement_set.order_by("typologie").all():
        logements_totale["sh_totale"] += logement.surface_habitable
        logements_totale["sa_totale"] += logement.surface_annexes
        logements_totale["sar_totale"] += logement.surface_annexes_retenue
        logements_totale["su_totale"] += logement.surface_utile
        logements_totale["loyer_total"] += logement.loyer
        if logement.typologie not in nb_logements_par_type:
            nb_logements_par_type[logement.get_typologie_display()] = 0
        nb_logements_par_type[logement.get_typologie_display()] += 1

    logement_edds, lot_num = _prepare_logement_edds(convention)
    # tester si il logement exists avant de commencer

    object_images, local_pathes = _get_object_images(doc, convention)

    context = {
        "convention": convention,
        "bailleur": convention.bailleur,
        "programme": convention.programme,
        "lot": convention.lot,
        "administration": convention.programme.administration,
        "logement_edds": logement_edds,
        "logements": convention.lot.logement_set.all(),
        "annexes": annexes,
        "stationnements": convention.lot.typestationnement_set.all(),
        "prets_cdc": convention.pret_set.filter(preteur__in=["CDCF", "CDCL"]),
        "autres_prets": convention.pret_set.exclude(preteur__in=["CDCF", "CDCL"]),
        "references_cadastrales": convention.programme.referencecadastrale_set.all(),
        **object_images,
        "nb_logements_par_type": nb_logements_par_type,
        "lot_num": lot_num,
        **_compute_mixte(convention),
        "loyer_m2": _get_loyer_par_metre_carre(convention),
        **logements_totale,
        "liste_des_annexes": _compute_liste_des_annexes(
            convention.lot.typestationnement_set.all(), annexes
        ),
    }

    jinja_env = jinja2.Environment()
    jinja_env.filters["d"] = _to_fr_date
    jinja_env.filters["f"] = _to_fr_float
    jinja_env.filters["pl"] = _pluralize
    jinja_env.filters["len"] = len
    doc.render(context, jinja_env)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    for local_path in list(set(local_pathes)):
        os.remove(local_path)

    return file_stream


def generate_pdf(file_stream, convention):
    # save the convention docx locally
    local_docx_path = str(settings.MEDIA_ROOT) + f"/convention_{convention.uuid}.docx"

    print("settings.CONVERTAPI_SECRET")
    print(settings.CONVERTAPI_SECRET)
    # get a pdf version
    if settings.CONVERTAPI_SECRET:
        with open(local_docx_path, "wb") as local_file:
            local_file.write(file_stream.read())
            local_file.close()

        convertapi.api_secret = settings.CONVERTAPI_SECRET
        result = convertapi.convert("pdf", {"File": local_docx_path})

        convention_dirpath = f"conventions/{convention.uuid}/convention_docs/"
        convention_filename = f"{convention.uuid}.pdf"
        pdf_path = _save_io_as_file(
            result.file.io, convention_dirpath, convention_filename
        )

        # remove docx version
        os.remove(local_docx_path)
    else:
        convention_dirpath = f"conventions/{convention.uuid}/convention_docs/"
        convention_filename = f"{convention.uuid}.docx"
        pdf_path = _save_io_as_file(
            file_stream, convention_dirpath, convention_filename
        )

    file_stream.seek(0)

    # END PDF GENERATION
    return pdf_path


def _save_io_as_file(file_io, convention_dirpath, convention_filename):

    if settings.DEFAULT_FILE_STORAGE == "django.core.files.storage.FileSystemStorage":
        if not os.path.exists(settings.MEDIA_URL + convention_dirpath):
            try:
                os.makedirs(settings.MEDIA_URL + convention_dirpath)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    pdf_path = f"{convention_dirpath}/{convention_filename}"
    destination = default_storage.open(
        pdf_path,
        "bw",
    )
    destination.write(file_io.getbuffer())
    destination.close()

    return pdf_path


def _to_fr_date(date):
    if date is None:
        return ""
    return date.strftime("%d/%m/%Y")


def _to_fr_float(value, d=2):
    if value is None:
        return ""
    return format(value, f",.{d}f").replace(",", " ").replace(".", ",")


def _pluralize(value):
    if value > 1:
        return "s"
    return ""


def _build_files_for_docx(doc, convention_uuid, file_list):
    # pylint: disable=R1732
    local_pathes = []
    docx_images = []
    files = UploadedFile.objects.filter(uuid__in=file_list)
    for object_file in files:  # convention.programme.vendeur_files().values():
        if "image" in object_file.content_type:
            file = default_storage.open(
                object_file.filepath(convention_uuid),
                "rb",
            )
            local_path = (
                settings.MEDIA_ROOT / f"{object_file.uuid}_{object_file.filename}"
            )
            local_file = open(local_path, "wb")
            local_file.write(file.read())
            file.close()
            local_file.close()
            docx_images.append(
                InlineImage(doc, image_descriptor=f"{local_path}", width=Inches(5))
            )
            local_pathes.append(f"{local_path}")
    return docx_images, local_pathes


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
    edd_volumetrique_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.edd_volumetrique_files()
    )
    object_images["edd_volumetrique_images"] = edd_volumetrique_images
    local_pathes += tmp_local_path
    edd_classique_images, tmp_local_path = _build_files_for_docx(
        doc, convention.uuid, convention.programme.edd_classique_files()
    )
    object_images["edd_classique_images"] = edd_classique_images
    local_pathes += tmp_local_path

    return object_images, local_pathes


def _get_loyer_par_metre_carre(convention):
    logement = convention.lot.logement_set.first()
    if logement:
        return convention.lot.logement_set.first().loyer_par_metre_carre
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
        mixite["mixPLUS_10pc"] = round(convention.lot.nb_logements * 0.1)
        mixite["mixPLUS_30pc"] = round(convention.lot.nb_logements * 0.3)
        if convention.lot.nb_logements < 10:
            mixite["mixPLUSinf10_30pc"] = round(convention.lot.nb_logements * 0.3)
            mixite["mixPLUSinf10_10pc"] = round(convention.lot.nb_logements * 0.1)
        else:
            mixite["mixPLUSsup10_30pc"] = round(convention.lot.nb_logements * 0.3)

    return mixite


def _prepare_logement_edds(convention):
    logement_edds = convention.programme.logementedd_set.order_by(
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
