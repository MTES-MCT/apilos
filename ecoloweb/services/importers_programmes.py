from typing import List, Optional

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


class ProgrammeImporter(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """

    model = Programme

    def _get_query_one(self) -> str:
        return self._get_file_content("resources/sql/programmes.sql")

    def _get_identity_keys(self) -> List[str]:
        return ["numero_galion"]

    def _get_o2o_dependencies(self):
        return {
            "bailleur": BailleurImporter,
            "administration": AdministrationImporter,
        }

    def _get_o2m_dependencies(self) -> List:
        return [ReferenceCadastraleImporter]


class LotImporter(ModelImporter):
    """
    Importer for the ProgrammeLot model, without one-to-one nor one-to-many dependency
    """

    model = Lot

    def _get_query_one(self) -> str:
        return self._get_file_content("resources/sql/programme_lots.sql")

    def _get_query_many(self) -> Optional[str]:
        return self._get_file_content("resources/sql/programme_lots_many.sql")

    def _get_o2o_dependencies(self):
        return {
            "programme": (ProgrammeImporter, False),
        }

    def _get_o2m_dependencies(self):
        return [LogementImporter, TypeStationnementImporter]


class LogementImporter(ModelImporter):
    model = Logement

    def _get_query_many(self) -> str:
        return self._get_file_content("resources/sql/programme_logements.sql")

    def _get_o2o_dependencies(self):
        return {
            "lot": (LotImporter, False),
        }

    def _prepare_data(self, data: dict) -> dict:
        if (surface_habitable := data.pop("surface_habitable")) is not None:
            data["surface_habitable"] = round(float(surface_habitable), 2)
        else:
            data["surface_habitable"] = None

        if (surface_annexes := data.pop("surface_annexes")) is not None:
            data["surface_annexes"] = round(float(surface_annexes), 2)
        else:
            data["surface_habitable"] = None

        if (surface_annexes_retenue := data.pop("surface_annexes_retenue")) is not None:
            data["surface_annexes_retenue"] = round(float(surface_annexes_retenue), 2)
        else:
            data["surface_annexes_retenue"] = None

        if (surface_utile := data.pop("surface_utile")) is not None:
            data["surface_utile"] = round(float(surface_utile), 2)
        else:
            data["surface_utile"] = None


class ReferenceCadastraleImporter(ModelImporter):
    model = ReferenceCadastrale

    def _prepare_data(self, data: dict) -> dict:
        superficie = data.pop("superficie", 0)

        data["surface"] = ReferenceCadastrale.compute_surface(superficie)

        return data

    def _get_query_many(self) -> Optional[str]:
        return self._get_file_content(
            "resources/sql/programme_reference_cadastrale.sql"
        )

    def _get_o2o_dependencies(self):
        return {
            "programme": (ProgrammeImporter, False),
        }


class TypeStationnementImporter(ModelImporter):
    model = TypeStationnement

    def _get_query_many(self) -> Optional[str]:
        return self._get_file_content("resources/sql/programme_type_stationnement.sql")

    def _get_o2o_dependencies(self):
        return {
            "lot": (LotImporter, False),
        }
