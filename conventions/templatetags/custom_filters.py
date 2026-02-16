import json
from re import compile as rcompile
from re import escape as rescape
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.http.request import HttpRequest
from django.template.defaulttags import register
from django.utils.safestring import mark_safe

from bailleurs.models import Bailleur
from conventions.models import ConventionStatut, PieceJointe
from core.utils import get_key_from_json_field, is_valid_uuid, strip_accents
from instructeurs.models import Administration
from programmes.models import Financement
from siap.siap_client.client import SIAPClient
from upload.models import UploadedFile
from users.models import GroupProfile


@register.filter(name="highlight_if_match")
def highlight_if_match(text: Any, search: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    if len(search) < 3:
        return text

    def _normalize(text: str) -> str:
        for c in ("-", "_", "/", ","):
            text = text.replace(c, " ")
        return " ".join(text.split()).lower()

    rgx = rcompile(rescape(_normalize(search)))
    match = rgx.search(_normalize(text))
    if match:
        start, end = match.span()
        text = f"{text[:start]}<span class='apilos-search-highlight'>{text[start:end]}</span>{text[end:]}"
        return mark_safe(text)

    return text


@register.filter
def is_bailleur(request: HttpRequest) -> bool:
    if "currently" in request.session:
        return request.session["currently"] in GroupProfile.bailleur_profiles()

    return request.user.is_bailleur()


@register.filter
def is_instructeur(request: HttpRequest) -> bool:
    if "currently" in request.session:
        return request.session["currently"] in GroupProfile.instructeur_profiles()
    return request.user.is_instructeur()


@register.filter
def is_readonly(request: HttpRequest) -> bool:
    # Manage is_staff exception
    if "readonly" in request.session:
        return request.session["readonly"]
    return False


@register.filter
def current_administration(request: HttpRequest) -> None | int:
    if is_instructeur(request) and request.session.get("administration"):
        administration = Administration.objects.get(
            id=request.session["administration"]["id"]
        )
        return administration.uuid
    return None


@register.filter
def current_bailleur(request: HttpRequest) -> None | int:
    if is_bailleur(request) and request.session.get("bailleur"):
        bailleur = Bailleur.objects.get(id=request.session["bailleur"]["id"])
        return bailleur.uuid
    return None


@register.filter
def display_administration(request: HttpRequest) -> bool:
    if (
        "multi_administration" in request.session
        and request.session["multi_administration"]
    ):
        return True
    return is_bailleur(request)


@register.filter
def get_manage_habilitation_url(request: HttpRequest) -> str:
    if settings.CERBERE_AUTH:
        client = SIAPClient.get_instance()
        # https://minlog-siap.gateway.intapi.recette.sully-group.fr/gerer-habilitations
        return f"{client.racine_url_acces_web}/gerer-habilitations" + (
            f"?habilitation_id={request.session['habilitation_id']}"
            if "habilitation_id" in request.session
            else ""
        )
    return ""


@register.filter
def get_menu_url(request: HttpRequest, menu_url: str) -> str:
    if settings.CERBERE_AUTH:
        client = SIAPClient.get_instance()
        target_url = ""
        if not menu_url.startswith("//") and not menu_url.startswith("http"):
            target_url = f"{client.racine_url_acces_web}"
        return f"{target_url}{menu_url}?habilitation_id={request.session['habilitation_id']}"
    return ""


@register.filter
def is_conventionnement_menu_url(menu_url: str) -> str:
    return settings.CERBERE_AUTH and (
        menu_url.endswith("/conventions") or menu_url == "/operation"
    )


@register.filter
def get_change_habilitation_url(request: HttpRequest, habilitation_id: int) -> str:
    client = SIAPClient.get_instance()
    if settings.CERBERE_AUTH:
        return (
            f"{client.racine_url_acces_web}{client.url_acces_web}"
            + f"?habilitation_id={habilitation_id}"
        )
    return ""


@register.filter
def get_siap_operation_url(request: HttpRequest, numero_operation: str) -> str:
    client = SIAPClient.get_instance()
    relative_path = client.url_acces_web_operation.replace(
        "<NUM_OPE_SIAP>", numero_operation
    )
    if settings.CERBERE_AUTH:
        return (
            f"{client.racine_url_acces_web}{relative_path}"
            + f"?habilitation_id={request.session['habilitation_id']}"
        )
    return ""


@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return ""
    return dictionary.get(key, "")


@register.filter
def has_own_active_comment(comments, user_id):
    return user_id in list(
        map(
            lambda x: x.user_id,
            filter(
                lambda comment: comment.statut != ConventionStatut.SIGNEE.label,
                comments,
            ),
        )
    )


@register.filter
def hasnt_active_comments(comments, object_field):
    object_comments = comments.get(object_field)
    if object_comments is None:
        return True
    return not (
        list(
            filter(
                lambda comment: (comment.statut != ConventionStatut.SIGNEE.label),
                object_comments,
            )
        )
    )


@register.filter
def has_comments(comments, object_field):
    return comments.get(object_field) is not None


@register.filter
def has_comments_with_prefix(comments, prefix):
    for comment_key in comments.keys():
        if comment_key.startswith(prefix):
            return True
    return False


@register.filter
def inline_text_multiline(text):
    if text is None:
        return ""
    if isinstance(text, str):
        return ", ".join(list(map(lambda t: t.strip().rstrip(","), text.split("\n"))))
    return text


@register.filter
def get_text_from_textfiles(field):
    return get_key_from_json_field(field, "text")


@register.filter
def get_files_from_textfiles(field):
    files = get_key_from_json_field(field, "files")
    if isinstance(files, dict):
        return [f for f in files.values() if "uuid" in f and is_valid_uuid(f["uuid"])]
    return None


@register.filter
def without_missing_files(files):
    if not files:
        return ""

    files_as_json = json.loads(files)
    for convention_id, file in files_as_json.items():
        try:
            UploadedFile.objects.get(uuid=convention_id, filename=file["filename"])
        except UploadedFile.DoesNotExist:
            del files_as_json[convention_id]

    return json.dumps(files_as_json)


@register.filter
def with_financement(convention):
    return Financement.SANS_FINANCEMENT not in [
        lot.financement for lot in convention.lots.all()
    ]


@register.filter
def display_comments(convention):
    return convention.statut in [
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
        ConventionStatut.A_SIGNER.label,
        ConventionStatut.SIGNEE.label,
    ]


@register.filter
def display_comments_summary(convention):
    return convention.statut in [
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    ]


@register.filter
def display_validation(convention, request):
    if not is_instructeur(request):
        return False
    if convention.statut in [
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    ]:
        return True
    return (
        convention.statut == ConventionStatut.PROJET.label
        and convention.cree_par is not None
        and convention.cree_par.is_instructeur()
    )


@register.filter
def display_is_validated(convention):
    return convention.statut in [
        ConventionStatut.A_SIGNER.label,
        ConventionStatut.SIGNEE.label,
        ConventionStatut.PUBLICATION_EN_COURS.label,
        ConventionStatut.PUBLIE.label,
        ConventionStatut.RESILIEE.label,
        ConventionStatut.DENONCEE.label,
    ]


@register.filter
def display_is_resiliated(convention):
    return (
        convention.statut
        in [
            ConventionStatut.RESILIEE.label,
        ]
        and not convention.is_avenant()
    )


@register.filter
def display_is_not_resiliated_or_denonciated(convention):
    return convention.statut not in [
        ConventionStatut.RESILIEE.label,
        ConventionStatut.DENONCEE.label,
    ]


@register.filter
def display_spf_info(convention):
    return (
        convention.date_envoi_spf is not None
        or convention.date_publication_spf is not None
    )


@register.filter
def display_notification_instructeur_to_bailleur(convention, request):
    return convention.statut in [
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    ] and is_instructeur(request)


@register.filter
def display_notification_bailleur_to_instructeur(convention, request):
    return convention.statut in [
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    ] and is_bailleur(request)


@register.filter
def display_notification_new_convention_instructeur_to_bailleur(convention, request):
    return (
        convention.statut == ConventionStatut.PROJET.label
        and is_instructeur(request)
        and convention.cree_par is not None
        and convention.cree_par.is_instructeur()
    )


@register.filter
def display_demande_correction(convention):
    return convention.statut == ConventionStatut.INSTRUCTION.label


@register.filter
def display_demande_instruction(convention):
    return convention.statut == ConventionStatut.CORRECTION.label


@register.filter
def display_redirect_sent(convention):
    return convention.statut == ConventionStatut.A_SIGNER.label


@register.filter
def display_redirect_project(convention):
    return settings.CERBERE_AUTH and convention.statut == ConventionStatut.PROJET.label


@register.filter
def display_redirect_post_action(convention):
    return convention.statut in [
        ConventionStatut.SIGNEE.label,
        ConventionStatut.PUBLICATION_EN_COURS,
        ConventionStatut.PUBLIE.label,
        ConventionStatut.DENONCEE.label,
        ConventionStatut.RESILIEE.label,
    ]


@register.filter
def display_redirect_convention_publie(convention):
    return convention.statut == ConventionStatut.PUBLIE.label


@register.filter
def display_redirect_convention_en_publication(convention):
    return convention.statut == ConventionStatut.PUBLICATION_EN_COURS.label


@register.filter
def display_convention_form_progressbar(convention):
    return convention.statut in [
        ConventionStatut.PROJET.label,
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    ]


@register.filter
def display_checkbox(convention, request):
    return (
        convention.is_avenant()
        and not request.session.get("readonly")
        and (
            convention.statut
            in [
                ConventionStatut.PROJET.label,
                ConventionStatut.INSTRUCTION.label,
                ConventionStatut.CORRECTION.label,
            ]
            or request.session.get("is_expert", False)
        )
    )


@register.filter
def display_type1and2(convention):
    return (
        convention.programme.bailleur.is_type1and2()
        and not convention.is_avenant()
        and not convention.programme.is_foyer
        and not convention.programme.is_residence
    )


@register.filter
def display_deactivated_because_type1and2_config_is_needed(convention):
    return display_type1and2(convention) and not convention.type1and2


@register.filter
def display_type1and2_editable(convention):
    return convention.statut in [
        ConventionStatut.PROJET.label,
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    ]


@register.filter
def not_op(boolean_value):
    return not boolean_value


@register.filter
def display_back_to_instruction(convention, request):
    return convention.statut in [
        ConventionStatut.A_SIGNER.label,
        ConventionStatut.SIGNEE.label,
    ] and is_instructeur(request)


@register.filter
def display_publication_button(convention):
    return convention.statut == ConventionStatut.SIGNEE.label


@register.filter
def display_submit_convention(convention, request):
    return convention.statut == ConventionStatut.PROJET.label and is_bailleur(request)


@register.filter
def display_delete_convention(convention):
    return convention.statut == ConventionStatut.ANNULEE.label


@register.filter
def display_cancel_convention(convention):
    return convention.statut in [
        ConventionStatut.PROJET.label,
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
    ]


@register.filter
def display_reactive_convention(convention):
    return convention.statut == ConventionStatut.ANNULEE.label


@register.filter
def display_create_avenant(convention):
    return not (
        {
            ConventionStatut.PROJET.label,
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
        }
        & {avenant.statut for avenant in convention.avenants.all()}
    )


@register.filter
def is_a_step(convention_form_step, classname):
    return any(
        step for step in convention_form_step.steps if step.classname == classname
    )


@register.filter
def get_text_as_list(text_field):
    if text_field is None:
        return ""
    return [line.strip(" -*") for line in text_field.splitlines() if line.strip(" -*")]


@register.filter
def to_query_params(data: dict):
    return urlencode(data)


@register.filter
def negate(condition: bool):
    return not condition


@register.filter
def attribute(object_from_template, key):
    """Gets an attribute of an object dynamically from a string key"""
    return getattr(object_from_template, key, None)


@register.filter
def can_promote(piece_jointe: PieceJointe):
    return piece_jointe.is_promotable()


@register.simple_tag
def administration_from(uuid):
    return Administration.objects.filter(uuid=uuid).first() or ""


@register.simple_tag
def bailleur_from(uuid):
    return Bailleur.objects.filter(uuid=uuid).first() or ""


@register.filter
def get_ordered_full_path(request, order_field):
    get_copy = request.GET.copy()
    if request.GET.get("order_by") == order_field:
        order_field = f"-{order_field}"
    get_copy["order_by"] = order_field
    get_copy["page"] = 1
    return f"{request.path}?{get_copy.urlencode()}"


@register.filter
def length_is(value, arg):
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False


@register.filter
def can_use_expert_mode(request, convention):
    is_readonly = "readonly" in request.session and request.session["readonly"]
    is_completed = convention.statut in ConventionStatut.completed_statuts()
    return is_completed and is_instructeur(request) and not is_readonly


@register.filter
def statut_is_signee(statut):
    return statut == ConventionStatut.SIGNEE.label


@register.filter
def statut_is_publied(statut):
    return statut == ConventionStatut.PUBLIE.label


@register.filter
def statut_is_in_publication(statut):
    return statut == ConventionStatut.PUBLICATION_EN_COURS.label


@register.filter
def siap_convention_step_doc_url(step: str) -> str | None:
    match strip_accents(step.lower()).replace(" ", "_"):
        case "bailleur":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/8093758/Bailleur+-+Conventionnement+APL"
        case "operation":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/7962720/Op+ration+-+Conventionnement+APL"
        case "cadastre":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/8093770/Cadastre+-+Conventionnement+APL"
        case "etats_descriptifs_de_division":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/8061055/EDD+-+Conventionnement+APL"
        case "financement":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/8028258/Financement+-+Conventionnement+APL"
        case "logements":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/8061069/Logements+-+Conventionnement+APL"
        case "annexes":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/7962734/Annexes+-+Conventionnement+APL"
        case "stationnements":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/8093790/Stationnements+-+Conventionnement+APL"
        case "commentaires":
            return "https://siap-logement.atlassian.net/wiki/spaces/ABDCS/pages/7962747/Commentaires+-+Conventionnement+APL"
        case _:
            return None
