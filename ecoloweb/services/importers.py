import os
import time

from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.db.models import Model
from django.template import Template, Context
from django.utils import timezone

from ecoloweb.models import EcoloReference
from ecoloweb.services.query_iterator import QueryResultIterator


class ModelImporter(ABC):
    """
    Base importer service class whose responsibility is to ensure imports of entities from Ecoloweb database of a single
    model.

    It relies on a SQL query to fetch and hydrate new models, with some extra layers like Ecolo references or identity
    fields to avoid duplicate imports.

    Thus, if one Ecolo entity has already been imported, changes that may have
    occurred in the meantime in the Ecolo database won't be echoed to the APiLos database /!\
    """
    ecolo_id_field = 'id'

    def __init__(self, debug=False):
        self._nb_imported_models: int = 0
        self._db_connection: CursorWrapper = connections['ecoloweb'].cursor()
        self.debug = debug

    @property
    @abstractmethod
    def model(self):
        """
        The model class manipulated by the importer to make find, get_or_create or create calls.

        Abstract property that must be overriden in children classes.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_sql_one_query(self) -> str:
        """
        Base method to declare SQL query for single model.
        """
        pass

    def _get_sql_many_query(self) -> Optional[str]:
        """
        Method to declare SQL query for many to one models.
        """
        return None

    def _debug(self, message: str):
        if self.debug:
            print(message)

    def _get_file_content(self, path):
        """
        Simple primitive method to extract file content as string.
        """
        return ''.join(open(os.path.join(os.path.dirname(__file__), path), 'r').readlines())

    def _get_sql_from_template(self, path: str, context: dict = {}):
        """
        Generate SQL query from a Django template file, using the input `context` dictionary
        """
        return Template(self._get_file_content(path)) \
            .render(Context(context | {'timezone': timezone.get_current_timezone()}))

    def _find_existing_model(self, data: dict) -> Optional[Model]:
        """
        Based on input data, attempts to extract an existing EcoloReference, using the `ecolo_id_field` defined as
        attribute and, if found, resolve it. See EcoloReference class model definition to understand how it works.

        The external reference in the Ecoloweb database is a string, as sometimes there is no other choice than to use a
        hashed value (like `md5` for Programe Lots for example).
        """
        if self.ecolo_id_field in data:
            ref = EcoloReference.objects.filter(
                apilos_model=EcoloReference.get_class_model_name(self.model),
                ecolo_id=data[self.ecolo_id_field]
            ).first()
            if ref is not None:
                return ref.resolve()

        return None

    def _register_ecolo_reference(self, instance: Model, ecolo_id: int, id: Optional[int] = None):
        """
        Create and save an EcoloReference model to mark an entity from the Ecoloweb database as imported
        """
        apilos_id = id if id is not None else instance.id

        EcoloReference.objects.create(
            apilos_model=EcoloReference.get_instance_model_name(instance),
            ecolo_id=str(ecolo_id),
            apilos_id=apilos_id
        )

    def _get_identity_keys(self) -> List[str]:
        """
        Return the list of field keys used to identify a model already existing in the APiLos database.

        This is basically the list of keys that will be used to perform a <model>.objects.get_or_create() call.

        In case there is no
        """
        return []

    def _get_matching_fields(self, data: dict) -> dict:
        if len(self._get_identity_keys()) > 0:
            return {key: data[key] for key in self._get_identity_keys() if data[key] is not None and data[key] != ''}

        return {}

    def _get_o2o_dependencies(self):
        """
        Return a dict of key -> ModelImportHandler

        This will replace fields with key `key` by their related model via the call of the related
        ModelImportHandler.import_one()
        """
        return {}

    def _fetch_related_o2o_objects(self, data) -> dict:
        """
        Hydrate the `data` dict by replacing external references (i.e. foreign keys) with the target
        object by using the _dependencies_ importers defined using `_get_dependencies`
        """
        for key, importer in self._get_o2o_dependencies().items():
            # First, try to resolve key suffixed by `_id` ...
            if f'{key}_id' in data:
                data[key] = importer.import_one(data.pop(f'{key}_id'))
            # ... else try to resolve key with its plain name
            elif key in data:
                data[key] = importer.import_one(data.pop(key))

        return data

    def _get_o2m_dependencies(self):
        """
        Return a dict of key -> ModelImportHandler

        This will replace fields with key `key` by their related model via the call of the related
        ModelImportHandler.import_one()
        """
        return {}

    def _fetch_related_o2m_objects(self, pk):
        """

        """
        for _, importer in self._get_o2m_dependencies().items():
            self._debug(f'Fetching o2m objects {importer.__class__.__name__} from {self.__class__.__name__} with FK {pk}')
            importer.import_many(pk)

    def _prepare_data(self, data: dict) -> dict:
        """
        Prepare data dict before it's used to create a new instance. This is where you can add, remove or update an
        attribute
        """
        return data

    def process_result(self, data: dict) -> Optional[Model]:
        """
        For each result row from the base SQL query, process it by following these steps:
        1. look for an already imported model and if found return it
        2. if some identity fields are declared in the `_get_identity_keys`, attempt to find a matching model from the
        APiLos database
        3. if still no model can be found, let's create it
        4. mark the newly created model as imported to avoid duplicate imports
        """
        self._debug(f'Prcessing result {data} for handler {self.__class__.__name__}')

        # Look for a potentially already imported model
        instance = self._find_existing_model(data)
        created = False
        # If model wasn't imported yet, import it now
        if instance is None:
            # Extract from data the id of the associated object in the Ecoloweb DB (in string format as it can be a
            # hash function like for programme lots)
            ecolo_id = data.pop(self.ecolo_id_field)
            # Compute data dictionary
            data = self._fetch_related_o2o_objects(data)
            data = self._prepare_data(data)

            # Extract dict values from declared identity keys as filters dict
            filters = self._get_matching_fields(data)
            if len(filters) > 0:
                instance, created = self.model.objects.get_or_create(**filters, defaults=data)

                self._register_ecolo_reference(instance, ecolo_id)
                if created:
                    self._nb_imported_models += 1

            else:
                # Create a new instance...
                instance = self.model.objects.create(**data)
                created = True
                # ...and mark it as imported
                self._register_ecolo_reference(instance, ecolo_id)
                self._nb_imported_models += 1

            if created:
                # Import one to many models
                self._fetch_related_o2m_objects(ecolo_id)

        return instance

    def import_one(self, pk) -> Optional[Model]:
        """
        Public entry point method to fetch a model from the Ecoloweb database based on its primary key
        """
        return self.process_result(
            self._query_single_row([pk])
        )

    def _query_single_row(self, parameters: List) -> Optional[Dict]:
        """
        Execute a SQL query returning a single result, as dict
        """
        start = time.time()
        self._debug(f'Start query for handler {self.__class__.__name__}')
        self._db_connection.execute(self._get_sql_one_query(), parameters)
        stop = time.time()
        self._debug(f'End query for handler {self.__class__.__name__} ({stop - start})')

        columns = [col[0] for col in self._db_connection.description]
        row = self._db_connection.fetchone()

        return dict(zip(columns, row)) if row else None

    def import_many(self, fk):
        """
        Public entry point method to fetch a list of models from the Ecoloweb database based on its foreign key
        """
        if self._get_sql_many_query() is not None:
            iterator = QueryResultIterator(
                self._db_connection,
                self._get_sql_many_query(),
                [fk]
            )

            for result in iterator:
                self.process_result(result)
