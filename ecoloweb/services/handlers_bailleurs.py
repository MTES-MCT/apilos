from typing import Optional

from django.db.models import Model

from .handlers import ModelImportHandler

from bailleurs.models import Bailleur


class BailleurImportHandler(ModelImportHandler):

    def _get_sql_query(self, criteria: dict) -> str:
        return self._get_sql_from_template('resources/sql/bailleurs.sql', criteria)

    def import_one(self, pk: int, importer: 'EcolowebImportService') -> Optional[Model]:
        return self._process_data(
            importer,
            self.query_single_row(
                self._get_sql_from_template('resources/sql/bailleurs.sql', {'pk': pk}),
                importer
            )
        )

    def _process_data(self, importer: 'EcolowebImportService', data: dict) -> Optional[Model]:
        ecolo_id = data.pop('id')

        if bailleur := self._find_ecolo_reference(Bailleur, ecolo_id) is None:
            bailleur, created = Bailleur.objects.get_or_create(siret=data['siret'], defaults=data)
            self._register_ecolo_reference(bailleur, ecolo_id)
        else:
            print(
                f"Skipping bailleur with ecolo id #{ecolo_id}, already imported ({ref.apilos_model} #{ref.apilos_id})")

            created = False

        if created:
            self.count += 1

        return bailleur

    def on_complete(self):
        print(f"Migrated {self.count} bailleur(s)")
