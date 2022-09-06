from typing import Tuple
from django.contrib.auth.models import Group
from django.conf import settings
from django.forms import model_to_dict
from django.http import HttpRequest
from siap.siap_client.utils import get_or_create_bailleur, get_or_create_administration
from siap.siap_client.client import SIAPClient
from users.models import Role, GroupProfile
from users.type_models import TypeRole


class CerbereSessionMiddleware:
    # pylint: disable=R0903
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # test if user is a siap user
        if request.user.is_authenticated and request.user.is_cerbere_user():
            # test if habilitations are set for the current user
            # if not, get it from SIAPClient

            if (
                "habilitation_id" in request.GET
                or "habilitations" not in request.session
            ):

                # get habilitation_id from params if exists
                habilitation_id = 0
                if "habilitation_id" in request.GET:
                    habilitation_id = int(request.GET.get("habilitation_id"))
                elif "habilitation_id" in request.session:
                    habilitation_id = request.session["habilitation_id"]
                client = SIAPClient.get_instance()

                # Set habilitation in session
                response = client.get_habilitations(
                    user_login=request.user.cerbere_login,
                    habilitation_id=habilitation_id,
                )
                habilitations = list(
                    filter(
                        lambda x: x["statut"] == "VALIDEE", response["habilitations"]
                    )
                )
                request.session["habilitations"] = habilitations

                if habilitation_id in map(lambda x: x["id"], habilitations):
                    request.session["habilitation_id"] = habilitation_id
                    request.session["habilitation"] = list(
                        filter(lambda x: x.get("id") == habilitation_id, habilitations)
                    )[0]
                elif habilitations:
                    request.session["habilitation_id"] = habilitations[0]["id"]
                    request.session["habilitation"] = habilitations[0]
                else:
                    raise Exception("Pas d'habilitation associéé à l'utilisateur")
                # Set habilitation in session
                _find_or_create_entity(request, request.session["habilitation"])

                if settings.NO_SIAP_MENU:
                    request.session["menu"] = None
                else:
                    response = client.get_menu(
                        user_login=request.user.cerbere_login,
                        habilitation_id=request.session["habilitation_id"],
                    )
                    request.session["menu"] = response["menuItems"]

            for key in ["bailleur", "currently", "administration", "role"]:
                request.user.siap_habilitation[key] = (
                    request.session[key] if key in request.session else None
                )

        response = self.get_response(request)

        return response


def _get_perimetre_geographique(from_habilitation: dict) -> Tuple[None, str]:
    perimetre_departement = perimetre_region = None
    if (
        "porteeTerritComp" in from_habilitation
        and "codePortee" in from_habilitation["porteeTerritComp"]
    ):
        if from_habilitation["porteeTerritComp"]["codePortee"] == "REG":
            perimetre_region = from_habilitation["porteeTerritComp"]["regComp"]["code"]
        if from_habilitation["porteeTerritComp"]["codePortee"] == "DEP":
            perimetre_departement = from_habilitation["porteeTerritComp"]["depComp"][
                "code"
            ]
    return (perimetre_departement, perimetre_region)


def _find_or_create_entity(request: HttpRequest, from_habilitation: dict):
    request.session["currently"] = from_habilitation["groupe"]["profil"]["code"]
    if from_habilitation["groupe"]["profil"]["code"] in [
        GroupProfile.SIAP_ADM_CENTRALE,
        GroupProfile.SIAP_SER_DEP,
        GroupProfile.SIAP_DIR_REG,
    ]:
        # Manage Role following the habilitation["groupe"]["codeRole"]
        (perimetre_departement, perimetre_region) = _get_perimetre_geographique(
            from_habilitation
        )
        Role.objects.filter(user=request.user).delete()
        role = Role.objects.create(
            typologie=TypeRole.ADMINISTRATEUR,
            user=request.user,
            group=Group.objects.get(name="administrateur"),
            perimetre_region=perimetre_region,
            perimetre_departement=perimetre_departement,
        )
        request.session["role"] = model_to_dict(role)

    if (
        from_habilitation["groupe"]["profil"]["code"]
        == GroupProfile.SIAP_MO_PERS_MORALE
    ):
        bailleur = get_or_create_bailleur(from_habilitation["entiteMorale"])
        request.session["bailleur"] = model_to_dict(
            bailleur,
            fields=[
                "id",
                "uuid",
                "siren",
                "nom",
            ],
        )
        # Manage Role following the habilitation["groupe"]["codeRole"]
        (perimetre_departement, perimetre_region) = _get_perimetre_geographique(
            from_habilitation
        )
        Role.objects.filter(user=request.user).delete()
        role = Role.objects.create(
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=request.user,
            group=Group.objects.get(name="bailleur"),
            perimetre_region=perimetre_region,
            perimetre_departement=perimetre_departement,
        )
        request.session["role"] = model_to_dict(role)

    if from_habilitation["groupe"]["profil"]["code"] == GroupProfile.SIAP_SER_GEST:
        # create if not exists gestionnaire
        administration = get_or_create_administration(from_habilitation["gestionnaire"])
        request.session["administration"] = model_to_dict(
            administration,
            fields=[
                "id",
                "uuid",
                "code",
                "nom",
            ],
        )
        (perimetre_departement, perimetre_region) = _get_perimetre_geographique(
            from_habilitation
        )
        Role.objects.filter(user=request.user).delete()
        role = Role.objects.create(
            typologie=TypeRole.INSTRUCTEUR,
            administration=administration,
            user=request.user,
            group=Group.objects.get(name="instructeur"),
            perimetre_region=perimetre_region,
            perimetre_departement=perimetre_departement,
        )
        request.session["role"] = model_to_dict(role)


habilitation = {
    "habilitations": [
        {
            "id": 40,
            "groupe": {
                "id": 19,
                "profil": {"code": "SER_GEST", "libelle": "Service gestionnaire"},
                "codeRole": "SERV_INSTR_DELGEG3_ADMIN",
                "libelleRole": "Administrateur",
                "codePorteeTerrit": "LOC",
                "isSignataire": False,
                "typeDelegation": "T3",
            },
            "gestionnaire": {
                "id": 9,
                "code": "13055",
                "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
                "typeDelegation": "3",
                "typeDelegataire": "1",
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-24",
            "dateDemande": "2022-06-24",
            "favori": False,
            "porteeTerritComp": {
                "id": 100,
                "codePortee": "EPCI",
                "regComp": {
                    "id": 15,
                    "code": "93",
                    "libelle": "Provence-Alpes-Côte d'Azur",
                },
                "depComp": {"id": 13, "code": "13", "libelle": "Bouches du Rhône"},
                "epciComp": {
                    "id": 276,
                    "code": "200054807",
                    "libelle": "Métropole d'Aix-Marseille-Provence",
                },
                "comComp": None,
                "libellee": "Métropole d'Aix-Marseille-Provence",
                "territoireIntervention": "Métropole d'Aix-Marseille-Provence",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "13055 - Métropole d'Aix-Marseille-Provence",
            "sousTitre2": None,
        },
        {
            "id": 46,
            "groupe": {
                "id": 28,
                "profil": {
                    "code": "MO_PERS_MORALE",
                    "libelle": "Maître d’ouvrage personne morale",
                },
                "codeRole": "MO_MORAL_REG_ADMIN",
                "libelleRole": "Administrateur délégué",
                "codePorteeTerrit": "REG",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": None,
                "code": None,
                "libelle": None,
                "typeDelegation": None,
                "typeDelegataire": None,
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": {
                "nom": "3F GRAND EST",
                "siren": "498273556",
                "commune": {"id": 27994, "code": None, "libelle": "Strasbourg"},
                "adresseLigne3": None,
                "adresseLigne4": "8 RUE ADOLPHE SEYBOTH",
                "adresseLigne6": "67000 STRASBOURG",
            },
            "dateExpiration": "2028-06-29",
            "dateDemande": "2022-06-29",
            "favori": False,
            "porteeTerritComp": {
                "id": 115,
                "codePortee": "REG",
                "regComp": {"id": 7, "code": "44", "libelle": "Grand Est"},
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "Grand Est",
                "territoireIntervention": "Grand Est",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "SIREN 498273556",
            "sousTitre2": "Grand Est",
        },
        {
            "id": 5,
            "groupe": {
                "id": 28,
                "profil": {
                    "code": "MO_PERS_MORALE",
                    "libelle": "Maître d’ouvrage personne morale",
                },
                "codeRole": "MO_MORAL_REG_ADMIN",
                "libelleRole": "Administrateur délégué",
                "codePorteeTerrit": "REG",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": None,
                "code": None,
                "libelle": None,
                "typeDelegation": None,
                "typeDelegataire": None,
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": {
                "nom": "13 HABITAT",
                "siren": "782855696",
                "commune": {
                    "id": 4527,
                    "code": None,
                    "libelle": "Marseille - 4e arrondissement",
                },
                "adresseLigne3": None,
                "adresseLigne4": "80 RUE ALBE",
                "adresseLigne6": "13004 MARSEILLE 4",
            },
            "dateExpiration": "2028-06-10",
            "dateDemande": "2022-06-10",
            "favori": False,
            "porteeTerritComp": {
                "id": 8,
                "codePortee": "REG",
                "regComp": {
                    "id": 15,
                    "code": "93",
                    "libelle": "Provence-Alpes-Côte d'Azur",
                },
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "Provence-Alpes-Côte d'Azur",
                "territoireIntervention": "Provence-Alpes-Côte d'Azur",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "SIREN 782855696",
            "sousTitre2": "Provence-Alpes-Côte d'Azur",
        },
        {
            "id": 62,
            "groupe": {
                "id": 6,
                "profil": {"code": "SER_DEP", "libelle": "Service départemental"},
                "codeRole": "SERV_DEP_ADMIN",
                "libelleRole": "Administrateur départemental",
                "codePorteeTerrit": "DEP",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": 215,
                "code": "DD042",
                "libelle": "DD042 - DDT Loire",
                "typeDelegation": None,
                "typeDelegataire": "3",
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-07-29",
            "dateDemande": "2022-07-29",
            "favori": False,
            "porteeTerritComp": {
                "id": 153,
                "codePortee": "DEP",
                "regComp": {"id": 14, "code": "84", "libelle": "Auvergne-Rhône-Alpes"},
                "depComp": {"id": 43, "code": "42", "libelle": "Loire"},
                "epciComp": None,
                "comComp": None,
                "libellee": "Loire",
                "territoireIntervention": "Loire",
            },
            "territComp": None,
            "statut": "A_VALIDER",
            "valide": False,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "DD042 - DDT Loire",
            "sousTitre2": None,
        },
        {
            "id": 3,
            "groupe": {
                "id": 1,
                "profil": {
                    "code": "ADM_CENTRALE",
                    "libelle": "Administration centrale",
                },
                "codeRole": "ADM_CENTRALE_ADMIN",
                "libelleRole": "Administrateur national",
                "codePorteeTerrit": "NAT",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": None,
                "code": None,
                "libelle": None,
                "typeDelegation": None,
                "typeDelegataire": None,
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-10",
            "dateDemande": "2022-06-10",
            "favori": False,
            "porteeTerritComp": {
                "id": 4,
                "codePortee": "NAT",
                "regComp": None,
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "France entière",
                "territoireIntervention": "France entière",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": None,
            "sousTitre2": "France entière",
        },
        {
            "id": 38,
            "groupe": {
                "id": 3,
                "profil": {"code": "DIR_REG", "libelle": "Direction régionale"},
                "codeRole": "DIR_REG_ADMIN",
                "libelleRole": "Administrateur régional",
                "codePorteeTerrit": "REG",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": 274,
                "code": "DR013",
                "libelle": "Provence-Alpes-Côte d'Azur",
                "typeDelegation": None,
                "typeDelegataire": "3",
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-23",
            "dateDemande": "2022-06-23",
            "favori": False,
            "porteeTerritComp": {
                "id": 96,
                "codePortee": "REG",
                "regComp": {
                    "id": 15,
                    "code": "93",
                    "libelle": "Provence-Alpes-Côte d'Azur",
                },
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "Provence-Alpes-Côte d'Azur",
                "territoireIntervention": "Provence-Alpes-Côte d'Azur",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "Provence-Alpes-Côte d'Azur",
            "sousTitre2": None,
        },
        {
            "id": 45,
            "groupe": {
                "id": 10,
                "profil": {"code": "SER_GEST", "libelle": "Service gestionnaire"},
                "codeRole": "SERV_INSTR_INSTRUCTEUR",
                "libelleRole": "Instructeur",
                "codePorteeTerrit": "LOC",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": 230,
                "code": "DD057",
                "libelle": "DD057 - DDT Moselle",
                "typeDelegation": None,
                "typeDelegataire": "3",
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-29",
            "dateDemande": "2022-06-29",
            "favori": False,
            "porteeTerritComp": {
                "id": 112,
                "codePortee": "DEP",
                "regComp": {"id": 7, "code": "44", "libelle": "Grand Est"},
                "depComp": {"id": 58, "code": "57", "libelle": "Moselle"},
                "epciComp": None,
                "comComp": None,
                "libellee": "Moselle",
                "territoireIntervention": "Moselle",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "DD057 - DDT Moselle",
            "sousTitre2": None,
        },
        {
            "id": 12,
            "groupe": {
                "id": 20,
                "profil": {"code": "SER_GEST", "libelle": "Service gestionnaire"},
                "codeRole": "SERV_INSTR_DELGEG3_INSTRUCTEUR",
                "libelleRole": "Instructeur",
                "codePorteeTerrit": "LOC",
                "isSignataire": False,
                "typeDelegation": "T3",
            },
            "gestionnaire": {
                "id": 9,
                "code": "13055",
                "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
                "typeDelegation": "3",
                "typeDelegataire": "1",
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-20",
            "dateDemande": "2022-06-20",
            "favori": False,
            "porteeTerritComp": {
                "id": 26,
                "codePortee": "EPCI",
                "regComp": {
                    "id": 15,
                    "code": "93",
                    "libelle": "Provence-Alpes-Côte d'Azur",
                },
                "depComp": {"id": 13, "code": "13", "libelle": "Bouches du Rhône"},
                "epciComp": {
                    "id": 276,
                    "code": "200054807",
                    "libelle": "Métropole d'Aix-Marseille-Provence",
                },
                "comComp": None,
                "libellee": "Métropole d'Aix-Marseille-Provence",
                "territoireIntervention": "Métropole d'Aix-Marseille-Provence",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "13055 - Métropole d'Aix-Marseille-Provence",
            "sousTitre2": None,
        },
        {
            "id": 41,
            "groupe": {
                "id": 22,
                "profil": {"code": "SER_GEST", "libelle": "Service gestionnaire"},
                "codeRole": "SERV_INSTR_DELGEG3_SIGNATAIRE",
                "libelleRole": "Signataire",
                "codePorteeTerrit": "LOC",
                "isSignataire": True,
                "typeDelegation": "T3",
            },
            "gestionnaire": {
                "id": 9,
                "code": "13055",
                "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
                "typeDelegation": "3",
                "typeDelegataire": "1",
                "typeLocalisation": None,
                "idDepartement": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-24",
            "dateDemande": "2022-06-24",
            "favori": False,
            "porteeTerritComp": {
                "id": 103,
                "codePortee": "EPCI",
                "regComp": {
                    "id": 15,
                    "code": "93",
                    "libelle": "Provence-Alpes-Côte d'Azur",
                },
                "depComp": {"id": 13, "code": "13", "libelle": "Bouches du Rhône"},
                "epciComp": {
                    "id": 276,
                    "code": "200054807",
                    "libelle": "Métropole d'Aix-Marseille-Provence",
                },
                "comComp": None,
                "libellee": "Métropole d'Aix-Marseille-Provence",
                "territoireIntervention": "Métropole d'Aix-Marseille-Provence",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "valide": True,
            "titre": "Préfet",
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "nicolas.oudard@beta.gouv.fr",
            },
            "sousTitre1": "13055 - Métropole d'Aix-Marseille-Provence",
            "sousTitre2": None,
        },
    ]
}
