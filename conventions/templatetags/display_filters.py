from django import template

register = template.Library()


@register.filter
def display_kind(convention):
    if convention.is_denonciation():
        return "dénonciation"
    if convention.is_avenant():
        return "avenant"
    return "convention"


@register.filter
def display_kind_with_cap(convention):
    if convention.is_denonciation():
        return "Dénonciation"
    if convention.is_avenant():
        return "Avenant"
    return "Convention"


@register.filter
def display_kind_with_pronom(convention):
    if convention.is_denonciation():
        return "la dénonciation"
    if convention.is_avenant():
        return "l'avenant"
    return "la convention"


@register.filter
def display_kind_with_pronom_with_cap(convention):
    if convention.is_denonciation():
        return "La dénonciation"
    if convention.is_avenant():
        return "L'avenant"
    return "La convention"


@register.filter
def display_kind_with_demonstratif(convention):
    if convention.is_denonciation():
        return "cette dénonciation"
    if convention.is_avenant():
        return "cet avenant"
    return "cette convention"


@register.filter
def display_kind_with_demonstratif_with_cap(convention):
    if convention.is_denonciation():
        return "Cette dénonciation"
    if convention.is_avenant():
        return "Cet avenant"
    return "Cette convention"


@register.filter
def display_kind_with_preposition(convention):
    if convention.is_denonciation():
        return "de dénonciation"
    if convention.is_avenant():
        return "d'avenant"
    return "de convention"


@register.filter
def display_pronom(convention):
    if convention.is_denonciation():
        return "la"
    if convention.is_avenant():
        return "le"
    return "la"


@register.filter
def display_pronom_with_cap(convention):
    if convention.is_denonciation():
        return "La"
    if convention.is_avenant():
        return "Le"
    return "La"


@register.filter
def display_personnal_pronom(convention):
    if convention.is_denonciation():
        return "elle"
    if convention.is_avenant():
        return "il"
    return "elle"


@register.filter
def display_personnal_pronom_with_cap(convention):
    if convention.is_denonciation():
        return "Elle"
    if convention.is_avenant():
        return "Il"
    return "Elle"


@register.filter
def display_gender_terminaison(convention):
    if convention.is_denonciation():
        return "e"
    if convention.is_avenant():
        return ""
    return "e"
