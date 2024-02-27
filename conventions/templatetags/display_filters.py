from django import template

from conventions.models import Convention

register = template.Library()


@register.filter
def display_kind(convention: Convention) -> str:
    if convention.is_denonciation:
        return "dénonciation"
    if convention.is_resiliation:
        return "résiliation"
    if convention.is_avenant():
        return "avenant"
    return "convention"


@register.filter
def display_kind_with_numero(convention: Convention) -> str:
    if convention.is_denonciation:
        return "dénonciation"
    if convention.is_resiliation:
        return "résiliation"
    if convention.is_avenant():
        return f"avenant {convention.numero}" if convention.numero else "avenant"
    return "convention"


@register.filter
def display_kind_with_pronom(convention: Convention) -> str:
    if convention.is_denonciation:
        return "la dénonciation"
    if convention.is_resiliation:
        return "la résiliation"
    if convention.is_avenant():
        return "l'avenant"
    return "la convention"


@register.filter
def display_kind_with_demonstratif(convention: Convention) -> str:
    if convention.is_denonciation:
        return "cette dénonciation"
    if convention.is_resiliation:
        return "cette résiliation"
    if convention.is_avenant():
        return "cet avenant"
    return "cette convention"


@register.filter
def display_kind_with_preposition(convention: Convention) -> str:
    if convention.is_denonciation:
        return "de dénonciation"
    if convention.is_resiliation:
        return "de résiliation"
    if convention.is_avenant():
        return "d'avenant"
    return "de convention"


@register.filter
def display_pronom(convention: Convention) -> str:
    if convention.is_denonciation or convention.is_resiliation:
        return "la"
    if convention.is_avenant():
        return "le"
    return "la"


@register.filter
def display_personnal_pronom(convention: Convention) -> str:
    if convention.is_denonciation or convention.is_resiliation:
        return "elle"
    if convention.is_avenant():
        return "il"
    return "elle"


@register.filter
def display_gender_terminaison(convention: Convention) -> str:
    if convention.is_denonciation or convention.is_resiliation:
        return "e"
    if convention.is_avenant():
        return ""
    return "e"
