from typing import List

from conventions.models import Convention, PieceJointe, PieceJointeType, AvenantType
from conventions.tasks import promote_piece_jointe
from .importers import ModelImporter
from .importers_programmes import ProgrammeImporter, LotImporter
from .query_iterator import QueryResultIterator


class ConventionImporter(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """

    model = Convention

    def _get_query_one(self) -> str | None:
        return self._get_file_content("resources/sql/conventions.sql")

    def _build_query_parameters(self, pk) -> list:
        args = pk.split(":")

        return [int(args[0]), args[1]]

    def _get_o2o_dependencies(self):
        return {
            "parent": self,
            "programme": (ProgrammeImporter, False),
            "lot": LotImporter,
        }

    def _get_o2m_dependencies(self) -> List:
        return [PieceJointeImporter]

    def get_all(self) -> QueryResultIterator:
        return QueryResultIterator(
            self._get_file_content("resources/sql/conventions_many.sql"),
            [self.departement],
            True,
        )

    def _on_processed(self, model: Convention | None):
        if model.is_avenant():
            # Avenant are automatically assigned to the type "commentaires"
            model.avenant_types.add(AvenantType.objects.get(nom="commentaires"))

        if model is not None:
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
                promote_piece_jointe.send(piece_jointe.id)


class PieceJointeImporter(ModelImporter):
    model = PieceJointe

    def _get_query_many(self) -> str | None:
        return self._get_file_content("resources/sql/convention_pieces_jointes.sql")

    def _get_o2o_dependencies(self):
        return {"convention": (ConventionImporter, False)}
