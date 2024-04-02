import datetime
import logging

from celery import shared_task
from django.conf import settings

from users.services import UserService

logger = logging.getLogger(__name__)


def _check_envoi():
    # Vérification tâches CRON activées
    if not settings.CRON_ENABLED:
        logger.warning("Tâches CRON désactivées, abandon")
        return False

    # Vérification que le jour est valide (1er lundi du mois)
    if datetime.date.today().weekday() > 0 or datetime.date.today().day > 7:
        logger.warning("Pas le premier lundi du mois, abandon")
        return False

    return True


@shared_task
def send_monthly_emails():

    if _check_envoi():

        if not settings.APPLICATION_DOMAIN_URL:
            raise Exception(
                "La variable APPLICATION_DOMAIN_URL doit être \
définie pour pouvoir envoyer des emails"
            )

        logger.warning("==================== Envoi des emails mensuels ")
        logger.warning("==================== Envoi des emails mensuels ")
        logger.warning("==================== Envoi des emails mensuels ")
        logger.warning("==================== Envoi des emails mensuels ")
        logger.warning("==================== Envoi des emails mensuels ")

        nb_sent_emails = UserService.email_mensuel()
        logger.warning(
            f"{nb_sent_emails['instructeur']} email(s) \
instructeur envoyé(s)"
        )
        logger.warning(
            f"{nb_sent_emails['bailleur']} email(s) bailleur \
envoyé(s)"
        )
