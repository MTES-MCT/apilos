import logging
from datetime import datetime

from typing import List

from conventions.models import Convention, PieceJointe, PieceJointeType, AvenantType
from conventions.services.file import ConventionFileService
from .importers import ModelImporter
from .importers_programmes import ProgrammeImporter, LotImporter
from .query_iterator import QueryResultIterator

logger = logging.getLogger(__name__)


class ConventionImporter(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """

    model = Convention

    def __init__(
        self,
        departement: str,
        import_date: datetime,
        with_dependencies=True,
        debug=False,
    ):
        super().__init__(departement, import_date, with_dependencies, debug)

    def _get_query_one(self) -> str | None:
        return self._get_sql_from_template("conventions.sql")

    def build_query_parameters(self, pk) -> list:
        args = pk.split(":")

        return [int(args[0]), args[1]]

    def _get_o2o_dependencies(self):
        return {
            "parent": self,
            "programme": ProgrammeImporter,
            "lot": LotImporter,
        }

    def _get_o2m_dependencies(self) -> List:
        return [(PieceJointeImporter, True)]

    def get_all(self) -> QueryResultIterator:
        return QueryResultIterator(
            self._get_sql_from_template("conventions_many.sql"),
            parameters=[self.departement],
        )

    def _prepare_data(self, data: dict) -> dict:
        programme_importer = ProgrammeImporter(
            departement=self.departement, import_date=self.import_date, debug=self.debug
        )
        data["programme"] = programme_importer.import_one(data.pop("programme_id"))

        lot_importer = LotImporter(
            departement=self.departement, import_date=self.import_date, debug=self.debug
        )
        data["lot"] = lot_importer.import_one(data.pop("lot_id"))

        parent_id = data.pop("parent_id")
        if parent_id is not None:
            print(parent_id)
            self.import_one(parent_id)

        return data

    def _on_processed(
        self, ecolo_id: str | None, model: Convention | None, created: bool
    ):
        if ecolo_id is not None:
            piece_jointe_importer = PieceJointeImporter(
                departement=self.departement,
                import_date=self.import_date,
                debug=self.debug,
            )
            piece_jointe_importer.import_many(
                piece_jointe_importer.build_query_parameters(ecolo_id)
            )

        if created and model is not None:
            if model.is_avenant():
                # Avenant are automatically assigned to the type "commentaires"
                model.avenant_types.add(AvenantType.objects.get(nom="commentaires"))
                model.save()

            piece_jointe = (
                model.pieces_jointes.filter(
                    type=PieceJointeType.AVENANT
                    if model.is_avenant()
                    else PieceJointeType.CONVENTION
                )
                .order_by("-cree_le")
                .first()
            )

            # Automatically promote the latest piece jointe with type CONVENTION as official convention document
            if piece_jointe is not None:
                try:
                    ConventionFileService.promote_piece_jointe(piece_jointe)
                except FileNotFoundError as e:
                    logger.info(
                        f"Unable to automatically upload PDF for convention {model.uuid}: {e}"
                    )


class PieceJointeImporter(ModelImporter):
    model = PieceJointe

    def _get_query_many(self) -> str | None:
        return self._get_file_content("resources/sql/convention_pieces_jointes.sql")

    def build_query_parameters(self, pk) -> list:
        args = pk.split(":")

        return [int(args[0]), args[1]]

    def _get_o2o_dependencies(self):
        return {"convention": (ConventionImporter, False)}

    def _prepare_data(self, data: dict) -> dict:
        convention_importer = ConventionImporter(
            departement=self.departement, import_date=self.import_date, debug=self.debug
        )
        data["convention"] = convention_importer.find_ecolo_reference(
            data.pop("convention_id")
        ).resolve()

        return data
