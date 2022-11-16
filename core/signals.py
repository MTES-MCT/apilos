import logging

from django.dispatch import receiver
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django_cas_ng.signals import cas_user_authenticated, cas_user_logout

logger = logging.getLogger(__name__)

# pylint: disable=W0613
@receiver(cas_user_authenticated)
def cas_user_authenticated_callback(sender, **kwargs):
    attributes = kwargs.get("attributes")
    logger.info(
        f'User logs in via CERBERE: user={kwargs.get("user")},'
        + f' cerbere_login={attributes.get("cerbere_login")},'
        + f' email={attributes.get("email")},'
        + f' username={attributes.get("username")}'
    )
    logger.debug("All login attributes : %s", kwargs)


@receiver(cas_user_logout)
def cas_user_logout_callback(sender, **kwargs):
    args = {}
    args.update(kwargs)

    logger.info(
        f'User logs in via CERBERE: user={kwargs.get("user")},'
        + f' session: {kwargs.get("session")},'
        + f' ticket: {kwargs.get("ticket")}'
    )
    logger.debug("All login attributes : %s", kwargs)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    logger.info(
        f"User logs in via Django authentication: user={user},"
        + f" email={user.email},"
        + f" username={user.username}"
    )


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    if user:
        logger.info(
            f"User logs out via Django authentication: user={user},"
            + f" email={user.email},"
            + f" username={user.username}"
        )
    else:
        logger.warning("Unlogged user tries to log out via Django authentication")


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    logger.info(
        "User logs in failed via Django authentication: identifiant=%s",
        credentials.get("username"),
    )
