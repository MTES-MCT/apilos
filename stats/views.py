from django.shortcuts import render
from django.db.models import (
    Count,
    Value,
    Sum,
    Case,
    When,
    Exists,
    OuterRef,
)
from django.db.models.functions import Substr, Concat

from bailleurs.models import Bailleur
from comments.models import Comment
from conventions.models import Convention
from programmes.models import Programme
from users.models import User


def index(request):
    query_by_statuses = (
        Convention.objects.all().values("statut").annotate(total=Count("statut"))
    )

    result = _get_conventions_by_dept()
    convention_by_status = {
        "Projet": 0,
        "Instruction_requise": 0,
        "Corrections_requises": 0,
        "A_signer": 0,
    }

    comments_champ = (
        Comment.objects.all()
        .values("nom_objet")
        .annotate(name=Concat("nom_objet", Value("-"), "champ_objet"))
        .values("name", "nom_objet", "champ_objet")
        .annotate(data=Count("champ_objet"))
        .order_by("-data", "nom_objet", "champ_objet")
    )
    comment_fields = []
    for qs in comments_champ:
        comment_fields.append(
            Comment(
                nom_objet=qs["nom_objet"], champ_objet=qs["champ_objet"]
            ).object_detail()
        )
    comment_data = []
    for qs in comments_champ:
        comment_data.append(qs["data"])

    users = User.objects.prefetch_related("role_set").all()
    bailleurs = users.filter(role__typologie="BAILLEUR").distinct()
    instructeurs = users.filter(role__typologie="INSTRUCTEUR").distinct()

    for query in query_by_statuses:
        convention_by_status[query["statut"][3:].replace(" ", "_")] = query["total"]

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
            "comment_fields": comment_fields,
            "comment_data": comment_data,
        },
    )


def _get_conventions_by_dept():
    """
    Return Conventions aggregated by deptartment and by status
    """
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
        "Projet": [],
        "Instruction_requise": [],
        "Corrections_requises": [],
        "A_signer": [],
        "Transmise": [],
    }
    for dept, statut_value in conv_bydept_bystatut.items():
        result["departement"].append(dept)
        for statut in [
            "1. Projet",
            "2. Instruction requise",
            "3. Corrections requises",
            "4. A signer",
            "5. Transmise",
        ]:
            result[statut[3:].replace(" ", "_")].append(
                statut_value[statut] if statut in statut_value else 0
            )
    return result


def get_null_fields():
    """
    Count null fields on not mandatory fields
    Bailleurs (with conventions):
    * capital_social
    Programmes (with conventions):
    * nb_locaux_commerciaux
    * nb_bureaux
    * autres_locaux_hors_convention
    """
    bailleurs = Bailleur.objects.filter(
        Exists(Convention.objects.filter(bailleur_id=OuterRef("pk")))
    ).aggregate(
        capital_social_count_null=Sum(
            Case(
                When(capital_social__isnull=True, then=1),
                When(capital_social__isnull=False, then=0),
            )
        ),
        count=Count("pk", distinct=True),
    )

    programmes = Programme.objects.filter(
        Exists(Convention.objects.filter(programme_id=OuterRef("pk")))
    ).aggregate(
        nb_locaux_commerciaux_count_null=Sum(
            Case(
                When(nb_locaux_commerciaux__isnull=True, then=1),
                When(nb_locaux_commerciaux__isnull=False, then=0),
            )
        ),
        nb_bureaux_count_null=Sum(
            Case(
                When(nb_bureaux__isnull=True, then=1),
                When(nb_bureaux__isnull=False, then=0),
            )
        ),
        autres_locaux_hors_convention_count_null=Sum(
            Case(
                When(autres_locaux_hors_convention__isnull=True, then=1),
                When(autres_locaux_hors_convention__isnull=False, then=0),
            )
        ),
        count=Count("pk", distinct=True),
    )
