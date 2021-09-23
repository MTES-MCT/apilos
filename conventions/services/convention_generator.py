import io
import jinja2
from docxtpl import DocxTemplate
from django.conf import settings

from programmes.models import (
    Financement,
    Annexe,
)


def to_fr_date(date):
    if date is None:
        return ""
    return date.strftime("%d/%m/%Y")


def to_fr_float(value, d=2):
    if value is None:
        return ""
    return format(value, f",.{d}f").replace(",", " ").replace(".", ",")


def generate_hlm(convention):
    annexes = (
        Annexe.objects.prefetch_related("logement")
        .filter(logement__lot_id=convention.lot.id)
        .all()
    )
    filepath = f"{settings.BASE_DIR}/documents/HLM-template.docx"
    doc = DocxTemplate(filepath)

    logements_totale = {
        "sh": 0,
        "sa": 0,
        "sar": 0,
        "su": 0,
        "loyer": 0,
    }
    nb_logements_par_type = {}
    for logement in convention.lot.logement_set.order_by("typologie").all():
        logements_totale["sh"] += logement.surface_habitable
        logements_totale["sa"] += logement.surface_annexes
        logements_totale["sar"] += logement.surface_annexes_retenue
        logements_totale["su"] += logement.surface_utile
        logements_totale["loyer"] += logement.loyer
        if logement.typologie not in nb_logements_par_type:
            nb_logements_par_type[logement.get_typologie_display()] = 0
        nb_logements_par_type[logement.get_typologie_display()] += 1

    logement_edds, lot_num = prepare_logement_edds(convention)
    mixite = compute_mixte(convention)
    # tester si il logement exists avant de commencer
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
        "nb_logements_par_type": nb_logements_par_type,
        "lot_num": lot_num,
        # 30 % au moins > 10 logement si PLUS
        "mixPLUSsup10_30pc": mixite[
            "mixPLUSsup10_30pc"
        ],  # 30 % plus de 10 logements si PLUS
        "mixPLUSinf10_30pc": mixite[
            "mixPLUSinf10_30pc"
        ],  # 30 % moins de 10 logements si PLUS
        "mixPLUSinf10_10pc": mixite[
            "mixPLUSinf10_10pc"
        ],  # 10 % moins de 10 logements si PLUS
        "mixPLUS_30pc": mixite["mixPLUS_30pc"],  # 30 % si PLUS
        "mixPLUS_10pc": mixite["mixPLUS_10pc"],  # 10 % si PLUS
        "loyer_m2": convention.lot.logement_set.first().loyer_par_metre_carre,
        "sh_totale": logements_totale["sh"],
        "sa_totale": logements_totale["sa"],
        "sar_totale": logements_totale["sar"],
        "su_totale": logements_totale["su"],
        "loyer_total": logements_totale["loyer"],
        "liste_des_annexes": compute_liste_des_annexes(
            convention.lot.typestationnement_set.all(), annexes
        ),
    }

    jinja_env = jinja2.Environment()
    jinja_env.filters["d"] = to_fr_date
    jinja_env.filters["f"] = to_fr_float
    jinja_env.filters["len"] = len
    doc.render(context, jinja_env)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    return file_stream


def compute_liste_des_annexes(typestationnements, annexes):
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


def compute_mixte(convention):
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


def prepare_logement_edds(convention):
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
