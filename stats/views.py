from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import Substr

from conventions.models import Convention
from users.models import User


def index(request):
    query_by_statuses = (
        Convention.objects.all().values("statut").annotate(total=Count("statut"))
    )
    queryset_bydept_bystatut = (
        Convention.objects.all()
        .annotate(departement=Substr("programme__code_postal", 1, 2))
        .values("departement", "statut")
        .annotate(total=Count("statut"))
        .order_by("departement")
    )

    conv_bydept_bystatut = {}
    for result_query in queryset_bydept_bystatut:
        if result_query["departement"] not in conv_bydept_bystatut:
            conv_bydept_bystatut[result_query["departement"]] = {}
        conv_bydept_bystatut[result_query["departement"]][
            result_query["statut"]
        ] = result_query["total"]
    result = {
        "departement": [],
        "BROUILLON": [],
        "INSTRUCTION": [],
        "CORRECTION": [],
        "VALIDE": [],
        "CLOS": [],
    }
    for dept, statut_value in conv_bydept_bystatut.items():
        result["departement"].append(dept)
        for statut in ["BROUILLON", "INSTRUCTION", "CORRECTION", "VALIDE", "CLOS"]:
            result[statut].append(statut_value[statut] if statut in statut_value else 0)

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
            "conv_bydept": result,
            "dept": str(result["departement"]),
        },
    )
