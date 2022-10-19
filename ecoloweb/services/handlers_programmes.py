from .handlers import ModelImportHandler

from bailleurs.models import Bailleur

from programmes.models import Programme, Lot, Logement


class ProgrammeImportHandler(ModelImportHandler):

    def _get_sql_query(self) -> str:
        return self._get_sql_from_template('resources/sql/programmes.sql', {'max_row': 10})

    def _process_row(self, data: dict) -> bool:
        # TODO: attach a real bailleur instead of a randomly picked one
        data['bailleur'] = Bailleur.objects.order_by('?').first()
        ecolo_id = data.pop('id')

        if ref := self._find_ecolo_reference(Programme, ecolo_id) is None:
            if data['numero_galion'] is not None:
                programme, created = Programme.objects.get_or_create(numero_galion=data['numero_galion'], defaults=data)
            else:
                programme = Programme.objects.create(**data)
                created = True
            self._register_ecolo_reference(programme, ecolo_id)
        else:
            print(f"Skipping Programme with ecolo id #{ecolo_id}, already imported ({ref.apilos_model} #{ref.apilos_id})")
            created = False

        return created

    def on_complete(self):
        print(f"Migrated {self.count} programme(s)")


class ProgrammeLotImportHandler(ModelImportHandler):

    def _get_sql_query(self) -> str:
        return self._get_sql_from_template('resources/sql/programme_lots.sql', {'max_row': 10})

    def _process_row(self, data: dict) -> bool:
        ecolo_id = data.pop('id')
        if ref := self._find_ecolo_reference(Programme, ecolo_id) is None:

            # TODO: attach a real bailleur instead of a randomly picked one
            data['bailleur'] = Bailleur.objects.order_by('?').first()
            data['programme'] = self._resolve_reference(Programme, data.pop('programme_id'))

            lot = Lot.objects.create(**data)
            created = True

            self._register_ecolo_reference(lot, ecolo_id)
        else:
            print(f"Skipping lot with ecolo id #{ecolo_id}, already imported ({ref.apilos_model} #{ref.apilos_id})")
            created = False

        return created

    def on_complete(self):
        print(f"Migrated {self.count} lot(s)")


class ProgrammeLogementImportHandler(ModelImportHandler):

    def _get_sql_query(self) -> str:
        return self._get_sql_from_template('resources/sql/programme_logements.sql', {'max_row': 10})

    def _process_row(self, data: dict) -> bool:
        ecolo_id = data.pop('id')
        if ref := self._find_ecolo_reference(Logement, ecolo_id) is None:

            # TODO: attach a real bailleur instead of a randomly picked one
            data['bailleur'] = Bailleur.objects.order_by('?').first()
            data['lot'] = self._resolve_reference(Lot, data.pop('lot_id'))

            logement = Logement.objects.create(**data)
            created = True

            self._register_ecolo_reference(logement, ecolo_id)
        else:
            print(f"Skipping logement with ecolo id #{ecolo_id}, already imported ({ref.apilos_model} #{ref.apilos_id})")
            created = False

        return created

    def on_complete(self):
        print(f"Migrated {self.count} logement(s)")
