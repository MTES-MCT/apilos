from .handlers import ModelImportHandler

from instructeurs.models import Administration


class AdministrationImportHandler(ModelImportHandler):

    def _get_sql_query(self, criteria: dict) -> str:
        return self._get_sql_from_file('resources/sql/administrations.sql')

    def _process_data(self, data: dict) -> bool:
        ecolo_id = data.pop('id')

        if ref := self._find_ecolo_reference(Administration, ecolo_id) is None:
            administration, created = Administration.objects.get_or_create(code=data['code'], defaults=data)
        else:
            print(
                f"Skipping administration with ecolo id #{ecolo_id}, already imported ({ref.apilos_model} #{ref.apilos_id})")
            created = False

        return created

    def on_complete(self):
        print(f"Migrated {self._count} administration(s)")
