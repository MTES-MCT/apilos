from django.http.request import HttpRequest
from django.conf import settings
from django.template.defaultfilters import date as _date
from django.template.defaulttags import register
from core import model_utils
from programmes.models import Financement
from siap.siap_client.client import SIAPClient
from conventions.models import ConventionStatut
from users.models import GroupProfile


@register.filter
def is_bailleur(request: HttpRequest) -> bool:
    return "currently" in request.session and request.session["currently"] in [
        GroupProfile.STAFF,
        GroupProfile.BAILLEUR,
        GroupProfile.SIAP_MO_PERS_MORALE,
        GroupProfile.SIAP_MO_PERS_PHYS,
    ]


@register.filter
def is_instructeur(request: HttpRequest) -> bool:
    return "currently" in request.session and request.session["currently"] in [
        GroupProfile.STAFF,
        GroupProfile.INSTRUCTEUR,
        GroupProfile.SIAP_SER_GEST,
        GroupProfile.SIAP_ADM_CENTRALE,
    ]


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
        return (
            f"{client.racine_url_acces_web}/gerer-habilitations"
            + f"?habilitation_id={request.session['habilitation_id']}"
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
def get_siap_operation_url(request: HttpRequest, numero_galion: str) -> str:
    client = SIAPClient.get_instance()
    relative_path = client.url_acces_web_operation.replace(
        "<NUM_OPE_SIAP>", numero_galion
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
            filter(lambda comment: comment.statut != ConventionStatut.SIGNEE, comments),
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
                lambda comment: (comment.statut != ConventionStatut.SIGNEE),
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
def is_administrator(current_user, user):
    return current_user.is_administrator(user)


@register.filter
def is_administration_administrator(current_user, administration):
    return current_user.is_administration_administrator(administration)


@register.filter
def is_bailleur_administrator(current_user, bailleur):
    return current_user.is_bailleur_administrator(bailleur)


@register.filter
def to_fr_date(date):
    """
    Display french date using the date function from django.template.defaultfilters
    Write the date in letter (ex : 5 janvier 2021). More about format syntax here :
    https://docs.djangoproject.com/fr/4.0/ref/templates/builtins/#date
    """
    if date is None:
        return ""
    return _date(date, "j F Y")


@register.filter
def to_fr_short_date(date):
    """
    Display french date using the date function from django.template.defaultfilters
    Write the date in number (ex : 05/01/2021). More about format syntax here :
    https://docs.djangoproject.com/fr/4.0/ref/templates/builtins/#date
    """
    if date is None:
        return ""
    return _date(date, "d/m/Y")


@register.filter
def get_text_from_textfiles(field):
    return model_utils.get_key_from_json_field(field, "text")


@register.filter
def get_files_from_textfiles(field):
    files = model_utils.get_key_from_json_field(field, "files")
    return files.values if files else None


@register.filter
def with_financement(convention):
    return convention.lot.financement != Financement.SANS_FINANCEMENT


@register.filter
def display_comments(convention):
    return convention.statut in [
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
        ConventionStatut.A_SIGNER,
        ConventionStatut.SIGNEE,
    ]


@register.filter
def display_comments_summary(convention):
    return convention.statut in [
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
    ]


@register.filter
def display_validation(convention, request):
    if not is_instructeur(request):
        return False
    if convention.statut in [ConventionStatut.INSTRUCTION, ConventionStatut.CORRECTION]:
        return True
    return (
        convention.is_project
        and convention.cree_par is not None
        and convention.cree_par.is_instructeur()
    )


@register.filter
def display_is_validated(convention):
    return convention.statut in [
        ConventionStatut.A_SIGNER,
        ConventionStatut.SIGNEE,
        ConventionStatut.RESILIEE,
    ]


@register.filter
def display_is_resiliated(convention):
    return convention.statut in [
        ConventionStatut.RESILIEE,
    ]


@register.filter
def display_notification_instructeur_to_bailleur(convention, request):
    return convention.statut in [
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
    ] and is_instructeur(request)


@register.filter
def display_notification_bailleur_to_instructeur(convention, request):
    return convention.statut in [
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
    ] and is_bailleur(request)


@register.filter
def display_notification_new_convention_instructeur_to_bailleur(convention, request):
    return (
        convention.statut == ConventionStatut.PROJET
        and is_instructeur(request)
        and convention.cree_par is not None
        and convention.cree_par.is_instructeur
    )


@register.filter
def display_demande_correction(convention):
    return convention.statut == ConventionStatut.INSTRUCTION


@register.filter
def display_demande_instruction(convention):
    return convention.statut == ConventionStatut.CORRECTION


@register.filter
def display_redirect_sent(convention):
    return convention.statut == ConventionStatut.A_SIGNER


@register.filter
def display_redirect_post_action(convention):
    return convention.statut == ConventionStatut.SIGNEE


@register.filter
def display_convention_form_progressbar(convention):
    return (
        convention.statut
        in [
            ConventionStatut.PROJET,
            ConventionStatut.INSTRUCTION,
            ConventionStatut.CORRECTION,
        ]
        and not convention.is_avenant()
    )


@register.filter
def display_type1and2_editable(convention):
    return convention.statut in [
        ConventionStatut.PROJET,
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
    ]


@register.filter
def display_back_to_instruction(convention, request):
    return convention.statut in [
        ConventionStatut.A_SIGNER,
        ConventionStatut.SIGNEE,
    ] and is_instructeur(request)
