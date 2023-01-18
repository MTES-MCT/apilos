from datetime import datetime
from typing import List

from . import SiretResolver
from .importers import ModelImporter
from bailleurs.models import Bailleur


class BailleurImporter(ModelImporter):
    model = Bailleur

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)

        try:
            self._siret_resolver = SiretResolver()
        except ConnectionRefusedError:
            self._siret_resolver = None

    def _get_query_one(self) -> str:
        return self._get_file_content("resources/sql/bailleurs.sql")

    def _get_identity_keys(self) -> List[str]:
        return ["siret"]

    def _resolve_siret(self, codesiren: str, date_creation: str):
        if self._siret_resolver:
            return self._siret_resolver.resolve(codesiren, date_creation)

        return None

    def _prepare_data(self, data: dict) -> dict:
        codesiret = data.pop("codesiret")
        codesiren = data.pop("codesiren")
        codepersonne = data.pop("codepersonne")
        date_creation = data["cree_le"]

        # Clean SIRET code
        if codesiret is not None:
            data["siret"] = codesiret

        elif (siret := self._resolve_siret(codesiren, date_creation)) is not None:
            data["siret"] = siret

        elif codesiren is not None:
            data["siret"] = codesiren

        else:
            data["siret"] = codepersonne

        return data
