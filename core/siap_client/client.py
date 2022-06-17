import datetime
import uuid
import threading
import requests
import jwt

from django.conf import settings

habilitation_mock = {
    "habilitations": [
        {
            "id": 9,
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
            "gestionnaire": {"id": None, "libelle": None, "typeDelegation": None},
            "sirenMo": "782855696",
            "dateExpiration": "2028-05-17",
            "dateDemande": "2022-05-17",
            "favori": False,
            "porteeTerritComp": {
                "id": 17,
                "codePortee": "REG",
                "regComp": {"id": 15, "libelle": "Provence-Alpes-Côte d'Azur"},
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "Provence-Alpes-Côte d'Azur",
            },
            "territComp": None,
            "statut": "VALIDEE",
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
            "id": 8,
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
            "gestionnaire": {"id": None, "libelle": None, "typeDelegation": None},
            "sirenMo": None,
            "dateExpiration": "2028-05-17",
            "dateDemande": "2022-05-17",
            "favori": False,
            "porteeTerritComp": {
                "id": 15,
                "codePortee": "NAT",
                "regComp": None,
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "France entière",
            },
            "territComp": None,
            "statut": "VALIDEE",
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
    ]
}

menu_mock = {
    "menuItems": [
        {
            "libelle": "Tableau de bord",
            "active": True,
            "url": "/tableau-bord",
            "menuItems": [],
        },
        {
            "libelle": "Habilitation",
            "active": True,
            "url": "/admin-habilitation",
            "menuItems": [
                {
                    "libelle": "Gestion des demandes",
                    "active": True,
                    "url": "/admin-habilitation/gestion-demandes-habilitation",
                    "menuItems": [],
                },
                {
                    "libelle": "Gestion des utilisateurs",
                    "active": True,
                    "url": "/admin-habilitation/gestion-utilisateurs",
                    "menuItems": [],
                },
            ],
        },
        {
            "libelle": "Mes opérations",
            "active": True,
            "url": "/operation",
            "menuItems": [
                {
                    "libelle": "Financement",
                    "active": True,
                    "url": "/operation/mes-operations",
                    "menuItems": [],
                },
                {
                    "libelle": "Conventionnement",
                    "active": True,
                    "url": "https://preprod.apilos.beta.gouv.fr/conventions",
                    "menuItems": [],
                },
            ],
        },
    ]
}

operation_mock = {
    "donneesMo": {
        "raisonSociale": "13 HABITAT",
        "siren": "782855696",
        "adresseL3Siege": None,
        "adresseL4Siege": "80 RUE ALBE",
        "adresseL6Siege": "13004 MARSEILLE 4",
        "codeFamilleMO": None,
    },
    "donneesLocalisation": {
        "region": {"codeInsee": "93", "libelle": None},
        "departement": {"codeInsee": "13", "libelle": None},
        "commune": {"codeInsee": "13210", "libelle": "Marseille - 10e arrondissement"},
        "adresse": " Allée de l’Aubepine 13010 Marseille",
        "zonage123": "02",
        "zonageABC": None,
    },
    "donneesOperation": {
        "nomOperation": "test",
        "numeroOperation": "20220600005",
        "aides": [
            {"code": "PLUS", "libelle": "PLUS"},
            {"code": "PLS", "libelle": "PLS"},
        ],
        "sousNatureOperation": "CNE",
        "typeConstruction": "TC_I",
        "natureLogement": "LOO",
    },
    "detailsOperation": [
        {
            "aide": {"code": "PLUS", "libelle": "PLUS"},
            "logement": {"nbLogementsIndividuels": 10, "nbLogementsCollectifs": None},
            "detailsTypeLogement": [
                {
                    "typeLogement": "T1",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1BIS",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1P",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T2",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T3",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T4",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T5",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T6",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
            ],
            "garages": [
                {
                    "type": "Enterrés / Sous-sol",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
                {
                    "type": "Superstructure",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
            ],
            "loyers": [
                {
                    "type": "Individuel",
                    "loyerZone": 0.0,
                    "loyerBase": 0.0,
                    "loyerReglementaire": 0.0,
                    "loyerPratique": 0,
                    "loyerGarages": [
                        {"type": "Enterrés / Sous-sol", "loyer": 0},
                        {"type": "Superstructure", "loyer": 0},
                    ],
                }
            ],
        },
        {
            "aide": {"code": "PLS", "libelle": "PLS"},
            "logement": {"nbLogementsIndividuels": 12, "nbLogementsCollectifs": None},
            "detailsTypeLogement": [
                {
                    "typeLogement": "T1",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1BIS",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1P",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T2",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T3",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T4",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T5",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T6",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
            ],
            "garages": [
                {
                    "type": "Enterrés / Sous-sol",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
                {
                    "type": "Superstructure",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
            ],
            "loyers": [
                {
                    "type": "Individuel",
                    "loyerZone": 0.0,
                    "loyerBase": 0.0,
                    "loyerReglementaire": 0.0,
                    "loyerPratique": 0,
                    "loyerGarages": [
                        {"type": "Enterrés / Sous-sol", "loyer": 0},
                        {"type": "Superstructure", "loyer": 0},
                    ],
                }
            ],
        },
    ],
    "planFinancement": {
        "subventions": [{"type": "PLUS", "montant": None}],
        "prets": [],
        "fondsPropres": 0.0,
    },
    "gestionnaire": None,
}


def _build_jwt(user_login: str = "", habilitation_id: int = 0) -> str:
    dt_iat = datetime.datetime.now()
    dt_exp = dt_iat + datetime.timedelta(minutes=5)
    ts_iat = int(dt_iat.timestamp())
    ts_exp = int(dt_exp.timestamp())
    payload = {
        "iat": ts_iat,
        "exp": ts_exp,
        "jti": str(uuid.uuid4()),
        "user-login": user_login,
    }
    if habilitation_id:
        payload["habilitation-id"] = habilitation_id

    return jwt.encode(
        payload,
        settings.SIAP_CLIENT_JWT_SIGN_KEY,
        algorithm=settings.SIAP_CLIENT_ALGORITHM,
    )


def _call_siap_api(
    route: str,
    base_route: str = "",
    user_login: str = "",
    habilitation_id: int = 0,
) -> requests.Response:
    siap_url_config = (
        settings.SIAP_CLIENT_HOST + base_route + settings.SIAP_CLIENT_PATH + route
    )
    myjwt = _build_jwt(user_login=user_login, habilitation_id=habilitation_id)
    response = requests.get(
        siap_url_config,
        headers={"siap-Authorization": f"Bearer {myjwt}"},
        timeout=5,
    )
    return response


class SIAPClient:

    __singleton_lock = threading.Lock()
    __singleton_instance = None

    # define the classmethod
    @classmethod
    def get_instance(cls):

        # check for the singleton instance
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    if settings.USE_MOCKED_SIAP_CLIENT:
                        print("SIAPClientMock")
                        cls.__singleton_instance = SIAPClientMock()
                    else:
                        print("SIAPClientRemote")
                        cls.__singleton_instance = SIAPClientRemote()

        # return the singleton instance
        return cls.__singleton_instance

    @classmethod
    def has_instance(cls):
        return bool(cls.__singleton_instance)


class SIAPClientInterface:
    def __init__(self) -> None:
        # pylint: disable=E1111
        config = self.get_siap_config()
        # {
        #     'racineUrlAccesWeb': 'http://siap-local.sully-group.fr/',
        #     'urlAccesWeb': '/tableau-bord',
        #     'urlAccesWebOperation':
        #       '/operation/mes-operations/editer/<NUM_OPE_SIAP>/informations-generales'
        # }
        self.racine_url_acces_web = config["racineUrlAccesWeb"].rstrip("/")
        self.url_acces_web = config["urlAccesWeb"]
        self.url_acces_web_operation = config["urlAccesWebOperation"]

    def get_siap_config(self) -> dict:
        pass

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        pass

    def get_menu(self, user_login: str, habilitation_id: int) -> dict:
        pass

    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict:
        pass


# Manage SiapClient as a Singleton
class SIAPClientRemote(SIAPClientInterface):
    def get_siap_config(self) -> dict:
        response = _call_siap_api("/config")
        return response.json()

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        response = _call_siap_api(
            "/habilitations",
            base_route="/services/habilitation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception(
            f"user doesn't have SIAP habilitation, SIAP error returned {response.content}"
        )

    def get_menu(self, user_login: str, habilitation_id: int = 0) -> dict:
        response = _call_siap_api(
            "/menu",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception(f"user doesn't have SIAP habilitation {response}")

    # /services/operation/api-int/v0/operation/{numeroOperation}
    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict:
        response = _call_siap_api(
            f"/operation/{operation_identifier}",
            base_route="/services/operation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception(
            f"user doesn't have enough rights to display operation {response}"
        )


# Manage SiapClient as a Singleton
class SIAPClientMock(SIAPClientInterface):
    def get_siap_config(self) -> dict:
        return {
            "racineUrlAccesWeb": "https://minlog-siap.gateway.intapi.recette.sully-group.fr",
            "urlAccesWeb": "/tableau-bord",
            "urlAccesWebOperation": (
                "/operation/mes-operations/editer/<NUM_OPE_SIAP>/informations-generales"
            ),
        }

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        return habilitation_mock

    def get_menu(self, user_login: str, habilitation_id: int = 0) -> dict:
        return menu_mock

    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict:
        return operation_mock
