from django.forms import model_to_dict
from rest_framework_simplejwt.authentication import JWTAuthentication

from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import get_or_create_bailleur, get_or_create_administration
from users.models import GroupProfile, User


class SIAPJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        client = SIAPClient.get_instance()
        habilitations = client.get_habilitations(
            user_login=validated_token["user-login"],
            habilitation_id=validated_token["habilitation-id"],
        )
        habilitation = list(
            filter(
                lambda x: x.get("id") == validated_token["habilitation-id"],
                habilitations["habilitations"],
            )
        )[0]
        user = User(cerbere_login=validated_token["user-login"])

        user.siap_habilitation["currently"] = habilitation["groupe"]["profil"]["code"]
        if habilitation["groupe"]["profil"]["code"] == GroupProfile.SIAP_MO_PERS_MORALE:
            bailleur = get_or_create_bailleur(habilitation["entiteMorale"])
            user.siap_habilitation["bailleur"] = model_to_dict(
                bailleur,
                fields=[
                    "id",
                    "uuid",
                    "siren",
                    "nom",
                ],
            )

        if habilitation["groupe"]["profil"]["code"] == GroupProfile.SIAP_SER_GEST:
            # create if not exists gestionnaire
            administration = get_or_create_administration(habilitation["gestionnaire"])
            user.siap_habilitation["administration"] = model_to_dict(
                administration,
                fields=[
                    "id",
                    "uuid",
                    "code",
                    "nom",
                ],
            )

        return user, validated_token
