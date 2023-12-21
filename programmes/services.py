import functools
from datetime import date

from django.db.models import Q

from programmes.models import IndiceEvolutionLoyer, NatureLogement
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import get_or_create_conventions


def get_or_create_conventions_from_operation_number(request, numero_operation):
    client = SIAPClient.get_instance()
    try:
        operation = client.get_operation(
            user_login=request.user.cerbere_login,
            habilitation_id=request.session["habilitation_id"],
            operation_identifier=numero_operation,
        )
    except SIAPException:
        # impossible to get operation from SIAP
        return (None, None, None)
    return get_or_create_conventions(operation, request.user)


class LoyerRedevanceUpdateComputer:
    @staticmethod
    def compute_loyer_update(
        montant_initial: float,
        nature_logement: str,
        date_initiale: date,
        date_actualisation: date | None = date.today(),
    ) -> float:
        if nature_logement not in NatureLogement.eligible_for_update():
            raise Exception(f"Nature de logement invalide {nature_logement}")

        qs = (
            IndiceEvolutionLoyer.objects.filter(
                nature_logement=nature_logement
                if nature_logement != NatureLogement.LOGEMENTSORDINAIRES
                else None,
                is_loyer=nature_logement == NatureLogement.LOGEMENTSORDINAIRES,
            )
            .filter(
                # Soit la plage de dates "englobe" la période
                Q(date_debut__gt=date_initiale, date_fin__lt=date_actualisation)
                |
                # Soit la date initiale est située sur la période
                Q(date_debut__lte=date_initiale, date_fin__gte=date_initiale)
            )
            .order_by("date_debut")
        )

        evolutions = list(qs.values_list("evolution", flat=True))

        return functools.reduce(
            lambda loyer, evolution: loyer * ((100.0 + evolution) / 100.0),
            evolutions,
            montant_initial,
        )
