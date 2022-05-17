import operator
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
from programmes.models import Lot, Programme
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

    null_fields = get_null_fields()
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
            "null_fields_keys": list(null_fields.keys()),
            "null_fields_values": list(null_fields.values()),
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

    programmes_qs = Programme.objects.filter(
        Exists(Convention.objects.filter(programme_id=OuterRef("pk")))
    ).annotate(
        count_referencecadastrale=Count("referencecadastrale"),
        count_logementedd=Count("logementedd"),
    )
    programmes = programmes_qs.aggregate(
        #
        # Opération
        #
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
        #
        # Référence Cadastrale
        #
        # permis_construire
        permis_construire_count_null=Sum(
            Case(
                When(permis_construire__isnull=True, then=1),
                When(permis_construire__isnull=False, then=0),
            )
        ),
        # date_acte_notarie
        date_acte_notarie_count_null=Sum(
            Case(
                When(date_acte_notarie__isnull=True, then=1),
                When(date_acte_notarie__isnull=False, then=0),
            )
        ),
        # date_achevement_previsible
        date_achevement_previsible_count_null=Sum(
            Case(
                When(date_achevement_previsible__isnull=True, then=1),
                When(date_achevement_previsible__isnull=False, then=0),
            )
        ),
        # date_achat
        date_achat_count_null=Sum(
            Case(
                When(date_achat__isnull=True, then=1),
                When(date_achat__isnull=False, then=0),
            )
        ),
        # date_achevement
        date_achevement_count_null=Sum(
            Case(
                When(date_achevement__isnull=True, then=1),
                When(date_achevement__isnull=False, then=0),
            )
        ),
        # vendeur
        vendeur_count_null=Sum(
            Case(
                When(vendeur__isnull=True, then=1),
                When(vendeur__isnull=False, then=0),
            )
        ),
        # acquereur
        acquereur_count_null=Sum(
            Case(
                When(acquereur__isnull=True, then=1),
                When(acquereur__isnull=False, then=0),
            )
        ),
        # reference_notaire
        reference_notaire_count_null=Sum(
            Case(
                When(reference_notaire__isnull=True, then=1),
                When(reference_notaire__isnull=False, then=0),
            )
        ),
        # reference_publication_acte
        reference_publication_acte_count_null=Sum(
            Case(
                When(reference_publication_acte__isnull=True, then=1),
                When(reference_publication_acte__isnull=False, then=0),
            )
        ),
        # acte_de_propriete
        acte_de_propriete_count_null=Sum(
            Case(
                When(acte_de_propriete__isnull=True, then=1),
                When(acte_de_propriete__isnull=False, then=0),
            )
        ),
        # certificat_adressage
        certificat_adressage_count_null=Sum(
            Case(
                When(certificat_adressage__isnull=True, then=1),
                When(certificat_adressage__isnull=False, then=0),
            )
        ),
        # effet_relatif
        effet_relatif_count_null=Sum(
            Case(
                When(effet_relatif__isnull=True, then=1),
                When(effet_relatif__isnull=False, then=0),
            )
        ),
        # reference_cadastrale
        reference_cadastrale_count_null=Sum(
            Case(
                When(reference_cadastrale__isnull=True, then=1),
                When(reference_cadastrale__isnull=False, then=0),
            )
        ),
        # mention_publication_edd_volumetrique
        mention_publication_edd_volumetrique_count_null=Sum(
            Case(
                When(mention_publication_edd_volumetrique__isnull=True, then=1),
                When(mention_publication_edd_volumetrique__isnull=False, then=0),
            )
        ),
        # mention_publication_edd_classique
        mention_publication_edd_classique_count_null=Sum(
            Case(
                When(mention_publication_edd_classique__isnull=True, then=1),
                When(mention_publication_edd_classique__isnull=False, then=0),
            )
        ),
        # reference_cadastrale
        # references_cadastrales_count_null=Sum(
        #     Case(
        #         When(count_referencecadastrale__lt=1, then=1),
        #         When(count_referencecadastrale__gt=0, then=0),
        #     )
        # ),
        count=Count("pk", distinct=True),
    )

    lots_qs = Lot.objects.filter(
        Exists(Convention.objects.filter(lot_id=OuterRef("pk")))
    ).annotate(
        count_logement=Count("logement"),
        #        count_annexe=Count("logement__annexe"),
    )
    lots = lots_qs.aggregate(
        # edd_volumetrique
        edd_volumetrique_count_null=Sum(
            Case(
                When(edd_volumetrique__isnull=True, then=1),
                When(edd_volumetrique__isnull=False, then=0),
            )
        ),
        # edd_classique
        edd_classique_count_null=Sum(
            Case(
                When(edd_classique__isnull=True, then=1),
                When(edd_classique__isnull=False, then=0),
            )
        ),
        count=Count("pk", distinct=True),
    )

    # edd_volumetrique
    # edd_classique

    null_fields = {
        "Bailleur - Capital Social": bailleurs["capital_social_count_null"]
        / bailleurs["count"]
        * 100,
        "Programme - Nombre de bureaux commerciaux": programmes[
            "nb_locaux_commerciaux_count_null"
        ]
        / programmes["count"]
        * 100,
        "Programme - Nombre de bureaux": programmes["nb_bureaux_count_null"]
        / programmes["count"]
        * 100,
        "Programme - Autres locaux hors convention": programmes[
            "autres_locaux_hors_convention_count_null"
        ]
        / programmes["count"]
        * 100,
        #
        # Cadastre
        #
        # permis_construire
        "Cadastre - permis_construire": programmes["permis_construire_count_null"]
        / programmes["count"]
        * 100,
        # date_acte_notarie
        "Cadastre - date_acte_notarie": programmes["date_acte_notarie_count_null"]
        / programmes["count"]
        * 100,
        # date_achevement_previsible
        "Cadastre - date_achevement_previsible": programmes[
            "date_achevement_previsible_count_null"
        ]
        / programmes["count"]
        * 100,
        # date_achat
        "Cadastre - date_achat": programmes["date_achat_count_null"]
        / programmes["count"]
        * 100,
        # date_achevement
        "Cadastre - date_achevement": programmes["date_achevement_count_null"]
        / programmes["count"]
        * 100,
        # vendeur
        "Cadastre - vendeur": programmes["vendeur_count_null"]
        / programmes["count"]
        * 100,
        # acquereur
        "Cadastre - acquereur": programmes["acquereur_count_null"]
        / programmes["count"]
        * 100,
        # reference_notaire
        "Cadastre - reference_notaire": programmes["reference_notaire_count_null"]
        / programmes["count"]
        * 100,
        # reference_publication_acte
        "Cadastre - reference_publication_acte": programmes[
            "reference_publication_acte_count_null"
        ]
        / programmes["count"]
        * 100,
        # acte_de_propriete
        "Cadastre - acte_de_propriete": programmes["acte_de_propriete_count_null"]
        / programmes["count"]
        * 100,
        # certificat_adressage
        "Cadastre - certificat_adressage": programmes["certificat_adressage_count_null"]
        / programmes["count"]
        * 100,
        # effet_relatif
        "Cadastre - effet_relatif": programmes["effet_relatif_count_null"]
        / programmes["count"]
        * 100,
        # reference_cadastrale
        "Cadastre - reference_cadastrale": programmes["reference_cadastrale_count_null"]
        / programmes["count"]
        * 100,
        # referencecadastrale
        "Cadastre - Tableau des références cadastrales": programmes_qs.filter(
            count_referencecadastrale=0
        ).count()
        / programmes["count"]
        * 100,
        # mention_publication_edd_volumetrique
        "EDD - mention_publication_edd_volumetrique": programmes[
            "mention_publication_edd_volumetrique_count_null"
        ]
        / programmes["count"]
        * 100,
        # mention_publication_edd_classique
        "EDD - mention_publication_edd_classique": programmes[
            "mention_publication_edd_classique_count_null"
        ]
        / programmes["count"]
        * 100,
        # edd_volumetrique
        "EDD - edd_volumetrique": lots["edd_volumetrique_count_null"]
        / lots["count"]
        * 100,
        # edd_classique
        "EDD - edd_classique": lots["edd_classique_count_null"] / lots["count"] * 100,
        # logementedd
        "Cadastre - Tableau des logements dans l'EDD simplifié": programmes_qs.filter(
            count_logementedd=0
        ).count()
        / programmes["count"]
        * 100,
    }

    sorted_null_fields = dict(
        sorted(null_fields.items(), key=operator.itemgetter(1), reverse=True)
    )

    return sorted_null_fields
