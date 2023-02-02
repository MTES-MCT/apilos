import logging
from datetime import datetime

from conventions.models import Convention, PieceJointe, PieceJointeType, AvenantType
from conventions.services.file import ConventionFileService
from programmes.models import Programme
from .importers import ModelImporter
from .importers_programmes import LotImporter
from .query_iterator import QueryResultIterator

logger = logging.getLogger(__name__)


class ConventionImporter(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """

    model = Convention

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)

        self._query_one = self._get_sql_from_template("conventions.sql")

        self._lot_importer = LotImporter(departement, import_date, debug)
        self._piece_jointe_importer = PieceJointeImporter(
            departement, import_date, debug
        )

    def build_query_parameters(self, pk) -> list:
        args = pk.split(":")

        return [int(args[0]), args[1]]

    def get_all(self) -> QueryResultIterator:
        return QueryResultIterator(
            self._get_sql_from_template("conventions_many.sql"),
            parameters=[self.departement],
        )

    def _prepare_data(self, data: dict) -> dict:
        return {
            "parent": self.import_one(data.pop("parent_id")),
            "lot": self._lot_importer.import_one(data.pop("lot_id")),
            "programme": self.resolve_ecolo_reference(
                ecolo_id=data.pop("programme_id"), model=Programme
            ),
            **data,
        }

    def _on_processed(
        self, ecolo_id: str | None, model: Convention | None, created: bool
    ):
        self._piece_jointe_importer.import_many(ecolo_id)

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

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)

        self._query_many = self._get_file_content(
            "resources/sql/convention_pieces_jointes.sql"
        )

    def build_query_parameters(self, pk) -> list:
        args = pk.split(":")

        return [int(args[0]), args[1]]

    def _prepare_data(self, data: dict) -> dict:
        return {
            "convention": self.resolve_ecolo_reference(
                data.pop("convention_id"), Convention
            ),
            **data,
        }
