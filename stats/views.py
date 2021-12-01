from django.shortcuts import render
from django.db.models import Count

from conventions.models import Convention
from users.models import User


def index(request):
    query_by_statuses = (
        Convention.objects.all().values("statut").annotate(total=Count("statut"))
    )

    convention_by_status = {
        "BROUILLON": 0,
        "INSTRUCTION": 0,
        "CORRECTION": 0,
        "VALIDE": 0,
    }

    users = User.objects.prefetch_related("role_set").all()
    bailleurs = users.filter(role__typologie="BAILLEUR").distinct()
    instructeurs = users.filter(role__typologie="INSTRUCTEUR").distinct()

    for query in query_by_statuses:
        convention_by_status[query["statut"]] = query["total"]
    return render(
        request,
        "stats/index.html",
        {
            "conventions_by_status": convention_by_status,
            "users_by_role": {
                "nb_instructeurs": instructeurs.count(),
                "nb_instructeurs_actifs": instructeurs.filter(
                    last_login__isnull=False
                ).count(),
                "nb_bailleurs": bailleurs.count(),
                "nb_bailleurs_actifs": bailleurs.filter(
                    last_login__isnull=False
                ).count(),
            },
        },
    )
