from collections import defaultdict

from django.db.models import Count

from programmes.models import Programme


def diff_programme_duplication(
    numero_operation: str, field_names: list[str] | None = None
) -> dict[str, list]:
    if field_names is None:
        field_names = [
            "code_postal",
            "ville",
            "administration_id",
            "bailleur_id",
            "count_lots",
        ]

    diff = defaultdict(list)

    qs = Programme.objects.filter(parent__isnull=True, numero_galion=numero_operation)

    if "count_lots" in field_names:
        qs = qs.annotate(count_logementedds=Count("lots"))

    for prog in qs.all():
        for f in field_names:
            value = getattr(prog, f, None)
            if value is not None:
                diff[f].append(value)

    return {k: sorted(list(set(v))) for k, v in diff.items() if len(set(v)) > 1}
