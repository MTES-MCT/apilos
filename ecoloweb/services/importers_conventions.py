import logging
from datetime import date

from django.db import transaction

from conventions.models import Convention, PieceJointe, PieceJointeType, AvenantType
from conventions.tasks import promote_piece_jointe
from programmes.models import Programme
from .importers import ModelImporter
from .importers_programmes import LotImporter
from .query_iterator import QueryResultIterator
from django.conf import settings

from ..models import EcoloReference

logger = logging.getLogger(__name__)


class ConventionImporter(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """

    model = Convention

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._query_one = self._get_sql_from_template("importers/convention.sql")

        self._lot_importer = LotImporter(
            departement, import_date, debug=debug, update=update
        )
        self._piece_jointe_importer = PieceJointeImporter(
            departement, import_date, debug=debug, update=update
        )

    def setup_db(self):
        with transaction.atomic("ecoloweb"):
            self._db_connection.execute(
                self._get_file_content("setup/convention_historique.sql")
            )

    def get_all(self) -> QueryResultIterator:
        if not self.update:
            ids_to_skip = list(
                EcoloReference.objects.filter(
                    apilos_model="conventions.Convention", departement=self.departement
                ).values_list("ecolo_id", flat=True)
            )

            return QueryResultIterator(
                "select ch.id from ecolo.ecolo_conventionhistorique ch where ch.departement = %s and not ch.id = any(%s) order by ch.conventionapl_id, ch.financement, ch.numero nulls first",
                parameters=[self.departement, ids_to_skip],
            )

        return QueryResultIterator(
            "select ch.id from ecolo.ecolo_conventionhistorique ch where ch.departement = %s order by ch.conventionapl_id, ch.financement, ch.numero nulls first",
            parameters=[self.departement],
        )

    def _prepare_data(self, data: dict) -> dict:
        parent_id = data.pop("parent_id")
        return {
            "parent": self.resolve_ecolo_reference(ecolo_id=parent_id, model=self.model)
            if parent_id is not None
            else None,
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

        if model is not None and not settings.TESTING:
            piece_jointe = None
            if model.is_avenant():
                # Avenant are automatically assigned to the type "commentaires"
                model.avenant_types.add(AvenantType.objects.get(nom="commentaires"))
                model.save()

                # Le PDF assigné à un avenant est celui de la n-ième pièce jointe par ordre de création de type AVENANT,
                # avec n le numéro de l'avenant
                numero = int(model.numero)

                if numero >= 1:
                    try:
                        piece_jointe = model.pieces_jointes.filter(
                            type=PieceJointeType.AVENANT
                        ).order_by("cree_le")[numero - 1]
                    except IndexError:
                        piece_jointe = None
            else:
                # Le PDF assigné à une convention est celui de la pièce jointe la plus récente de type CONVENTION
                piece_jointe = (
                    model.pieces_jointes.filter(type=PieceJointeType.CONVENTION)
                    .order_by("-cree_le")
                    .first()
                )

            # Automatically promote the latest piece jointe with type CONVENTION as official convention document
            if piece_jointe is not None:
                promote_piece_jointe.delay(piece_jointe.id)


class PieceJointeImporter(ModelImporter):
    model = PieceJointe

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._query_many = self._get_file_content("importers/pieces_jointes.sql")

    def _prepare_data(self, data: dict) -> dict:
        return {
            "convention": self.resolve_ecolo_reference(
                data.pop("convention_id"), Convention
            ),
            **data,
        }
