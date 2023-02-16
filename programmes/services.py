import functools
from datetime import date

from programmes.models import IndiceEvolutionLoyer
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import get_or_create_conventions


def get_or_create_conventions_from_operation_number(request, numero_operation):
    client = SIAPClient.get_instance()
    operation = client.get_operation(
        user_login=request.user.cerbere_login,
        habilitation_id=request.session["habilitation_id"],
        operation_identifier=numero_operation,
    )
    return get_or_create_conventions(operation, request.user)


class LoyerRedevanceUpdateComputer:
    @staticmethod
    def compute_loyer_update(
        montant_initial: float,
        nature_logement: str,
        date_initiale: date,
        date_actualisation: date | None = date.today(),
    ) -> float:
        coefficients = (
            IndiceEvolutionLoyer.objects.filter(
                annee__gt=date_initiale.year, annee__lte=date_actualisation.year
            )
            .order_by("annee")
            .values_list("coefficient", flat=True)
        )

        return functools.reduce(
            lambda loyer, coefficient: loyer * ((100 + coefficient) / 100),
            coefficients,
            montant_initial,
        )
