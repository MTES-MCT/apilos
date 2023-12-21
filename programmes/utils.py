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
            "count_logementedds",
            "count_referencecadastrales",
            "nb_lots",
        ]

    diff = defaultdict(list)

    for prog in (
        Programme.objects.filter(parent__isnull=False, numero_galion=numero_operation)
        .annotate(count_lots=Count("lots"))
        .annotate(count_logementedds=Count("logementedds"))
        .annotate(count_referencecadastrales=Count("referencecadastrales"))
        .all()
    ):
        for f in field_names:
            value = getattr(prog, f, None)
            if value is not None:
                diff[f].append(value)

    return {k: list(set(v)) for k, v in diff.items() if len(set(v)) > 1}
