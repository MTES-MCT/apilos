import logging
import datetime
import uuid
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
        "habilitation-id": habilitation_id,
    }
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
    logging.warn(f"API call : {siap_url_config}")
    logging.warn(f"JWT : {myjwt}")
    response = requests.get(
        siap_url_config,
        headers={"siap-Authorization": f"Bearer {myjwt}"},
    )
    logging.warn(f"API response : {response}")
    logging.warn(f"API response content : {response.content}")
    return response


class SIAPClient:

    __singleton_instance = None

    # define the classmethod
    @classmethod
    def get_instance(cls):

        # check for the singleton instance
        if not cls.__singleton_instance:
            if settings.USE_MOCKED_SIAP_CLIENT:
                logging.warn("SIAPClientMock")
                cls.__singleton_instance = SIAPClientMock()
            else:
                logging.warn("SIAPClientRemote")
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
    # pylint: disable=R0201

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
        raise Exception("user doesn't have SIAP habilitation")

    def get_menu(self, user_login: str, habilitation_id: int = 0) -> dict:
        response = _call_siap_api(
            "/menu2",
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
    # pylint: disable=R0201

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
        return {}
