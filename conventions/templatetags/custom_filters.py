from django.template.defaulttags import register


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
            filter(lambda comment: comment.statut != "CLOS", comments),
        )
    )


@register.filter
def hasnt_active_comments(comments, object_field):
    object_comments = comments.get(object_field)
    if object_comments is None:
        return True
    return not (
        list(filter(lambda comment: (comment.statut != "CLOS"), object_comments))
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
