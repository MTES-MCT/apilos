import datetime
import logging
from typing import Any

from celery import shared_task
from django.conf import settings

from users.services import UserService

logger = logging.getLogger(__name__)


@shared_task
def send_monthly_emails(no_verify: bool = False) -> dict[str, Any] | None:
    if not settings.APPLICATION_DOMAIN_URL:
        logger.warning(
            "La variable APPLICATION_DOMAIN_URL doit être définie pour pouvoir envoyer des emails, abandon."
        )
        return

    if not no_verify:
        # Vérification que le jour est valide (1er lundi du mois)
        if datetime.date.today().weekday() > 0 or datetime.date.today().day > 7:
            return

        if not settings.CRON_ENABLED:
            logger.warning("Tâches CRON désactivées, abandon.")
            return

    logger.warning(
        f"{'=' * 67}\n{'>' * 20} Envoi des emails mensuels {'<' * 20}\n{'=' * 67}"
    )

    nb_sent_emails = UserService.email_mensuel()

    logger.warning(f"{nb_sent_emails['instructeur']} email(s) instructeur envoyé(s)")
    logger.warning(f"{nb_sent_emails['bailleur']} email(s) bailleur envoyé(s)")

    return nb_sent_emails
