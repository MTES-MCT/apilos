import logging

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from siap.custom_middleware import (
    copy_session_habilitation_to_user,
    set_habilitation_in_session,
)
from users.models import User

logger = logging.getLogger(__name__)


class SIAPSimpleJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        logger.warning(
            "[SIAP call] METHOD : %s, PATH: %s, JWT TOKEN : %s",
            request.method,
            request.path,
            raw_token,
        )

        validated_token = self.get_validated_token(raw_token)
        return User(), validated_token


class SIAPJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        try:

            # Create user
            user = User(cerbere_login=validated_token["user-login"])
            request.user = user

            # Manage SIAP habilitation in session
            habilitation_id = validated_token["habilitation-id"]
            cerbere_login = validated_token["user-login"]

            # Set habilitation in session
            set_habilitation_in_session(
                request, cerbere_login, habilitation_id, session_only=True
            )

            copy_session_habilitation_to_user(request)

        except (KeyError, IndexError) as e:
            raise AuthenticationFailed(
                "User or Habilitation not found", code="user_not_found"
            ) from e
        return user, validated_token
