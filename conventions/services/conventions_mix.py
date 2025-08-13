import logging

from django.http import HttpRequest

from conventions.models.convention import Convention
from programmes.models.models import Lot, Programme

logger = logging.getLogger(__name__)


class OperationConventionMix:
    numero_operation: str
    requets: HttpRequest

    def __init__(self, request: HttpRequest, list_of_uuids_conventions) -> None:
        self.request = request
        self.list_of_uuids_conventions = list_of_uuids_conventions
        self.related_simple_conventions = Convention.objects.filter(
            uuid__in=self.list_of_uuids_conventions
        )

    def get_first_convention(self) -> Convention:
        return self.related_simple_conventions.first()

    def get_or_create_lots(self, convention_mixte) -> list[Lot]:
        if convention_mixte.lots:
            logger.error("lot not created alredy exist !!")
            return convention_mixte.lots
        lots = [
            convention.lot.clone(convention_mixte)
            for convention in list(self.related_simple_conventions)
        ]
        logger.error(f"lots created --> {lots}")
        convention_mixte.lots.set(lots)
        return lots

    def get_programme(self) -> Programme:
        return self.get_first_convention().programme

    def get_or_create_conventions_mixte(self):
        if not self.list_of_uuids_conventions:
            raise Exception("We can't create a mixte convention")

        self.programme = self.get_programme()
        conventions_mixte = Convention.objects.filter(
            programme=self.programme, type_convention="Mixte"
        )
        if not conventions_mixte:
            self.convention_mixte = Convention.objects.create(
                programme=self.programme,
                cree_par=self.request.user,
                type_convention="Mixte",
            )
            logger.error(
                f"the mixte convention is created {self.convention_mixte} with type {self.convention_mixte.type_convention}"
            )
        else:
            logger.error(
                f"the mixte convention is alredy exist {self.convention_mixte} : {self.convention_mixte.uuid} with type {self.convention_mixte.type_convention}"
            )

        self.lots = self.get_or_create_lots(self.convention_mixte)
        return (self.programme, self.lots, self.convention_mixte)
