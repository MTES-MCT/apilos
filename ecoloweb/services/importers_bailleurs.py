from datetime import datetime, date

from . import SiretResolver
from .importers import ModelImporter
from bailleurs.models import Bailleur

from django.conf import settings


class BailleurImporter(ModelImporter):
    model = Bailleur

    def __init__(
        self,
        departement: str,
        import_date: datetime,
        debug=False,
    ):
        super().__init__(departement, import_date, debug)

        try:
            self._siret_resolver = SiretResolver(settings.INSEE_API_KEY, settings.INSEE_API_SECRET)
        except BaseException:
            self._siret_resolver = None

        self._identity_keys = ["siret"]

        self._query_one = self._get_file_content("resources/sql/bailleurs.sql")

    def _resolve_siret(self, codesiren: str, date_creation: date):
        if self._siret_resolver:
            try:
                return self._siret_resolver.resolve(codesiren, date_creation)
            except BaseException:
                return None

        return None

    def _prepare_data(self, data: dict) -> dict:
        codesiret = data.pop("codesiret")
        date_creation = data["cree_le"]

        # Clean SIRET code
        if codesiret is not None:
            if data["nature_bailleur"] == "Bailleurs privés" or len(codesiret) == 14:
                data["siret"] = codesiret
            elif (siret := self._resolve_siret(codesiret, date_creation)) is not None:
                data["siret"] = siret

        return data
