from .handlers import ModelImportHandler

from conventions.models import Convention

from programmes.models import Programme, Lot
from .handlers_bailleurs import BailleurImportHandler


class ConventionImportHandler(ModelImportHandler):

    def _get_sql_query(self, criteria: dict) -> str:
        return self._get_sql_from_template('resources/sql/conventions.sql', criteria)

    def _process_data(self, importer: 'EcolowebImportService', data: dict) -> bool:
        ecolo_id = data.pop('id')

        if ref := self._find_ecolo_reference(Convention, ecolo_id) is None:

            data['bailleur'] = BailleurImportHandler().import_one(data.pop('bailleur_id'), importer)
            data['lot'] = Lot.objects.order_by('?').first()
            data['programme'] = Programme.objects.order_by('?').first()

            print(data['bailleur'])

            convention = Convention.objects.create(**data)
            created = True

            self._register_ecolo_reference(convention, ecolo_id)
        else:
            print(
                f"Skipping convention with ecolo id #{ecolo_id}, already imported ({ref.apilos_model} #{ref.apilos_id})")
            created = False

        return created

    def on_complete(self):
        print(f"Migrated {self.count} convention(s)")
