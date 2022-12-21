from typing import List

from django.db.models import Model

from conventions.models import Convention, PieceJointe, PieceJointeType
from conventions.services.file import ConventionFileService
from .importers import ModelImporter
from .importers_programmes import ProgrammeImporter, ProgrammeLotImporter
from .query_iterator import QueryResultIterator


class ConventionImporterSimple(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """
    model = Convention

    def _get_query_one(self) -> str | None:
        return self._get_file_content('resources/sql/conventions.sql')


class ConventionImporter(ConventionImporterSimple):

    def _get_o2o_dependencies(self):
        return {
            'programme': ProgrammeImporter,
            'lot': ProgrammeLotImporter,
        }

    def _get_o2m_dependencies(self) -> List:
        return [PieceJointeImporter]

    def get_all_by_departement(self) -> QueryResultIterator:
        return QueryResultIterator(
            self._db_connection,
            self._get_file_content('resources/sql/conventions_many.sql'),
            [self.departement]
        )

    def _on_processed(self, model: Convention | None):
        if model is not None:
            piece_jointe = model.pieces_jointes.filter(type=PieceJointeType.CONVENTION).order_by('-cree_le').first()
            # Automatically promote the latest piece jointe with type CONVENTION as official convention document
            if piece_jointe is not None:
                ConventionFileService.promote_piece_jointe_async(piece_jointe.id)


class PieceJointeImporter(ModelImporter):
    model = PieceJointe

    def _get_query_many(self) -> str | None:
        return self._get_file_content('resources/sql/convention_pieces_jointes.sql')

    def _get_o2o_dependencies(self):
        return {
            'convention': ConventionImporterSimple
        }
