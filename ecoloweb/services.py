import os

from abc import ABC, abstractmethod
from typing import List, Optional

from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.db.models import Model
from django.template import Template, Context
from django.utils import timezone

from bailleurs.models import Bailleur
from conventions.models import Convention
from ecoloweb.models import EcoloReference
from programmes.models import Programme, Lot, Logement


class ModelImportHandler(ABC):
    connection: CursorWrapper
    count: int = 0

    def __init__(self, connection: CursorWrapper):
        self.connection = connection

    @abstractmethod
    def _get_sql_query(self) -> str:
        pass

    def _get_file_content(self, path):
        return ''.join(open(os.path.join(os.path.dirname(__file__), path), 'r').readlines())

    def _get_sql_from_template(self, path: str, context: dict = {}):
        return Template(self._get_file_content(path))\
            .render(Context(context | {'timezone': timezone.get_current_timezone()}))

    def _get_sql_from_file(self, path: str) -> str:
        return self._get_file_content(path)

    def _find_ecolo_reference(self, clazz, ecolo_id: int)-> Optional[EcoloReference]:
        return EcoloReference.objects.filter(
            apilos_model=EcoloReference.get_class_model_name(clazz),
            ecolo_id=ecolo_id
        ).first()

    def _resolve_reference(self, clazz, ecolo_id: int)-> Optional[Model]:
        if ref := self._find_ecolo_reference(clazz, ecolo_id) is None:
            return None

        return ref.resolve()

    def _register_ecolo_reference(self, instance: Model, ecolo_id: int, id: Optional[int] = None):
        apilos_id = id if id is not None else instance.id

        EcoloReference.objects.create(
            apilos_model=EcoloReference.get_instance_model_name(instance),
            ecolo_id=ecolo_id,
            apilos_id=apilos_id
        )

    @abstractmethod
    def _process_row(self, data: dict) -> bool:
        pass

    def handle(self):
        count: int = 0

        # Run query
        self.connection.execute(self._get_sql_query())
        # Extract metadata to be able to convert each row into a dict
        columns = [col[0] for col in self.connection.description]

        # To reduce memory allocation we fetch rows 1 by 1
        while (row := self.connection.fetchone()) is not None:
            data = dict(zip(columns, row))
            self.count += 1 if self._process_row(data) else 0

        self.on_complete()

    def on_complete(self):
        pass


class ProgrammeImportHandler(ModelImportHandler):

    def _get_sql_query(self) -> str:
        return self._get_sql_from_template('resources/sql/programmes.sql')

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


class ConventionImportHandler(ModelImportHandler):

    def _get_sql_query(self) -> str:
        return self._get_sql_from_template('resources/sql/conventions.sql', {'max_row': 10})

    def _process_row(self, data: dict) -> bool:
        ecolo_id = data.pop('id')
        if ref := self._find_ecolo_reference(Convention, ecolo_id) is None:
            data['bailleur'] = Bailleur.objects.order_by('?').first()
            data['lot'] = Lot.objects.order_by('?').first()
            data['programme'] = Programme.objects.order_by('?').first()

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


class EcolowebImportService:
    """
    Service en charge de transférer les données depuis la base Ecoloweb vers la base APiLos
    """
    connection: CursorWrapper
    handlers: List[ModelImportHandler]

    def __init__(self, connection='ecoloweb'):
        self.connection: CursorWrapper = connections[connection].cursor()
        self.handlers = [
            # TODO manager dependencies between handlers (ex: ProgrammeLotImportHandler requires ProgrammeImportHandler)
            #ProgrammeImportHandler(self.connection),
            #ProgrammeLotImportHandler(self.connection),
            #ProgrammeLogementImportHandler(self.connection)
            ConventionImportHandler(self.connection)
        ]

    def process(self):
        for handler in self.handlers:
            handler.handle()
