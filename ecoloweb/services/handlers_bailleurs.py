from .handlers import ModelImportHandler

from bailleurs.models import Bailleur


class BailleurImportHandler(ModelImportHandler):

    def _get_sql_query(self) -> str:
        return self._get_sql_from_template('resources/sql/bailleurs.sql', {'max_row': 10})

    def _process_row(self, data: dict) -> bool:
        ecolo_id = data.pop('id')

        if ref := self._find_ecolo_reference(Bailleur, ecolo_id) is None:
            bailleur, created = Bailleur.objects.get_or_create(siret=data['siret'], defaults=data)
            self._register_ecolo_reference(bailleur, ecolo_id)
        else:
            print(
                f"Skipping bailleur with ecolo id #{ecolo_id}, already imported ({ref.apilos_model} #{ref.apilos_id})")
            created = False

        return created

    def on_complete(self):
        print(f"Migrated {self.count} bailleur(s)")
