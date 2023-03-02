from datetime import date

from django.db.models import Model

from programmes.models import (
    Programme,
    Lot,
    Logement,
    ReferenceCadastrale,
    TypeStationnement,
)

from .importers import ModelImporter
from .importers_administrations import AdministrationImporter
from .importers_bailleurs import BailleurImporter


class ReferenceCadastraleImporter(ModelImporter):
    model = ReferenceCadastrale

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._query_many = self._get_file_content(
            "importers/references_cadastrales.sql"
        )

    def _prepare_data(self, data: dict) -> dict:
        return {
            "surface": ReferenceCadastrale.compute_surface(data.pop("superficie", 0)),
            "programme": self.resolve_ecolo_reference(
                ecolo_id=data.pop("programme_id"), model=Programme
            ),
            **data,
        }


class TypeStationnementImporter(ModelImporter):
    model = TypeStationnement

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._query_many = self._get_file_content("importers/types_stationnement.sql")

    def _prepare_data(self, data: dict) -> dict:
        return {
            "lot": self.resolve_ecolo_reference(ecolo_id=data.pop("lot_id"), model=Lot),
            **data,
        }


class ProgrammeImporter(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """

    model = Programme

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._query_one = self._get_file_content("importers/programme.sql")

        self._bailleur_importer = BailleurImporter(
            departement, import_date, debug=debug, update=update
        )
        self._administration_importer = AdministrationImporter(
            departement, import_date, debug=debug, update=update
        )
        self._reference_cadastrale_importer = ReferenceCadastraleImporter(
            departement, import_date, debug=debug, update=update
        )

    def _prepare_data(self, data: dict) -> dict:
        parent_id = data.pop("parent_id")
        return {
            "parent": self.resolve_ecolo_reference(ecolo_id=parent_id, model=self.model)
            if parent_id is not None
            else None,
            "bailleur": self._bailleur_importer.import_one(data.pop("bailleur_id")),
            "administration": self._administration_importer.import_one(
                data.pop("administration_id")
            ),
            **data,
        }

    def _on_processed(self, ecolo_id: str | None, model: Model | None, created: bool):
        self._reference_cadastrale_importer.import_many(ecolo_id)


class LotImporter(ModelImporter):
    """
    Importer for the ProgrammeLot model, without one-to-one nor one-to-many dependency
    """

    model = Lot

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._query_one = self._get_file_content("importers/lot.sql")

        self._programme_importer = ProgrammeImporter(
            departement, import_date, debug=debug, update=update
        )
        self._logement_importer = LogementImporter(
            departement, import_date, debug=debug, update=update
        )
        self._type_stationnement_importer = TypeStationnementImporter(
            departement, import_date, debug=debug, update=update
        )

    def _prepare_data(self, data: dict) -> dict:
        parent_id = data.pop("parent_id")

        return {
            "parent": self.resolve_ecolo_reference(ecolo_id=parent_id, model=self.model)
            if parent_id is not None
            else None,
            "programme": self._programme_importer.import_one(data.pop("programme_id")),
            "surface_habitable_totale": self._rounded_value(
                data.pop("surface_habitable_totale")
            ),
            **data,
        }

    def _on_processed(self, ecolo_id: str | None, model: Model | None, created: bool):
        self._logement_importer.import_many(ecolo_id)
        self._type_stationnement_importer.import_many(ecolo_id)


class LogementImporter(ModelImporter):
    model = Logement

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._query_many = self._get_file_content("importers/logement.sql")

    def _prepare_data(self, data: dict) -> dict:
        return {
            "surface_habitable": self._rounded_value(data.pop("surface_habitable")),
            "surface_annexes": self._rounded_value(data.pop("surface_annexes")),
            "loyer_par_metre_carre": self._rounded_value(
                data.pop("loyer_par_metre_carre")
            ),
            "loyer": self._rounded_value(data.pop("loyer")),
            "surface_annexes_retenue": self._rounded_value(
                data.pop("surface_annexes_retenue")
            ),
            "surface_utile": self._rounded_value(data.pop("surface_utile")),
            "surface_corrigee": self._rounded_value(data.pop("surface_corrigee")),
            "lot": self.resolve_ecolo_reference(data.pop("lot_id"), Lot),
            **data,
        }
