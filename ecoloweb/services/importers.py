import os
import re
import time
from datetime import datetime

from typing import Dict, Type
from abc import ABC, abstractmethod

from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.db.models import Model
from django.template import Context, Engine
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

    ecolo_id_field: str = "id"

    def __init__(
        self,
        departement: str,
        import_date: datetime,
        debug=False,
    ):
        self._nb_imported_models: int = 0
        self._db_connection: CursorWrapper = connections["ecoloweb"].cursor()
        self.debug = debug
        self.departement = departement
        self.import_date = import_date
        self.engine = Engine(
            dirs=[os.path.join(os.path.dirname(__file__), "resources/sql")]
        )

        self._query_one = None
        self._query_many = None

        self._identity_keys = []

    @property
    @abstractmethod
    def model(self):
        """
        The model class manipulated by the importer to make find, get_or_create or create calls.

        Abstract property that must be overriden in children classes.
        """
        raise NotImplementedError

    def _debug(self, message: str):
        if self.debug:
            print(message)

    def _get_file_content(self, path):
        """
        Simple primitive method to extract file content as string.
        """
        return "".join(
            [
                re.sub("--.*", "", line)
                for line in open(
                    os.path.join(os.path.dirname(__file__), path), "r"
                ).readlines()
            ]
        )

    def _get_sql_from_template(self, path: str, context=None):
        """
        Generate SQL query from a Django template file, using the input `context` dictionary
        """
        if context is None:
            context = {}
        return self.engine.render_to_string(
            path, Context(context | {"timezone": timezone.get_current_timezone()})
        )

    def find_ecolo_reference(
        self, ecolo_id: str, model: Type[Model] | None = None
    ) -> EcoloReference | None:
        """
        Based on input data, attempts to extract an existing EcoloReference, using the `ecolo_id_field` defined as
        attribute and, if found, resolve it. See EcoloReference class model definition to understand how it works.

        The external reference in the Ecoloweb database is a string, as sometimes there is no other choice than to use a
        hashed value (like `md5` for Programme Lots for example).
        """
        return EcoloReference.objects.filter(
            apilos_model=EcoloReference.get_class_model_name(
                model if model is not None else self.model
            ),
            ecolo_id=ecolo_id,
        ).first()

    def resolve_ecolo_reference(
        self, ecolo_id: str, model: Type[Model] | None = None
    ) -> Model | None:
        ecolo_reference = self.find_ecolo_reference(ecolo_id, model)

        return ecolo_reference.resolve() if ecolo_reference is not None else None

    def _register_ecolo_reference(
        self, instance: Model, ecolo_id: int, id: int | None = None
    ):
        """
        Create and save an EcoloReference model to mark an entity from the Ecoloweb database as imported
        """
        EcoloReference.objects.create(
            apilos_model=EcoloReference.get_instance_model_name(instance),
            ecolo_id=str(ecolo_id),
            apilos_id=id if id is not None else instance.id,
            departement=self.departement,
            importe_le=self.import_date,
        )

    def _get_matching_fields(self, data: dict) -> dict:
        if len(self._identity_keys) > 0:
            return {
                key: data[key]
                for key in self._identity_keys
                if data[key] is not None and data[key] != ""
            }

        return {}

    def _prepare_data(self, data: dict) -> dict:
        """
        Prepare data dict before it's used to create a new instance. This is where you can add, remove or update an
        attribute
        """
        return data

    def process_result(self, data: dict | None) -> Model | None:
        """
        For each result row from the base SQL query, process it by following these steps:
        1. look for an already imported model and if found return it
        2. if some identity fields are declared in the `_get_identity_keys`, attempt to find a matching model from the
        APiLos database
        3. if still no model can be found, let's create it
        4. mark the newly created model as imported to avoid duplicate imports
        """
        if data is None:
            return None

        self._debug(f"Processing result {data} for handler {self.__class__.__name__}")

        # Look for a potentially already imported model
        ecolo_ref = (
            self.find_ecolo_reference(data[self.ecolo_id_field])
            if self.ecolo_id_field in data
            else None
        )
        created = True
        instance = None

        # If model wasn't imported yet, import it now
        if ecolo_ref is None:
            # Extract from data the id of the associated object in the Ecoloweb DB (in string format as it can be a
            # hash function like for programme lots)
            ecolo_id = data.pop(self.ecolo_id_field)

            # Compute data dictionary
            data = self._prepare_data(data)

            # Extract dict values from declared identity keys as filters dict
            filters = self._get_matching_fields(data)
            if len(filters) > 0:
                instance, created = self.model.objects.get_or_create(
                    **filters, defaults=data
                )

                self._register_ecolo_reference(instance, ecolo_id)
                if created:
                    self._nb_imported_models += 1

            else:
                # Create a new instance...
                if data is not None:
                    instance = self.model.objects.create(**data)

                    # ...and mark it as imported
                    self._register_ecolo_reference(instance, ecolo_id)
                    self._nb_imported_models += 1
        else:
            ecolo_id = ecolo_ref.ecolo_id
            instance = ecolo_ref.resolve()
            created = False

        self._on_processed(ecolo_id, instance, created)

        return instance

    def _on_processed(self, ecolo_id: str | None, model: Model | None, created: bool):
        pass

    def build_query_parameters(self, pk) -> list:
        return [pk]

    def import_one(self, pk: str | int | None) -> Model | None:
        """
        Public entry point method to fetch a model from the Ecoloweb database based on its primary key
        """
        if pk is None:
            return None

        ecolo_ref = self.find_ecolo_reference(pk)

        # If an EcoloReference has been found ...
        if ecolo_ref is not None:
            # ... return the associated model
            return ecolo_ref.resolve()

        # Otherwise perform SQL query and process result
        return self.process_result(
            self._query_single_row(self.build_query_parameters(pk))
        )

    def _query_single_row(self, parameters) -> Dict | None:
        """
        Execute a SQL query returning a single result, as dict
        """
        if self._query_one is None:
            raise NotImplementedError

        start = time.time()
        self._debug(
            f"Start query for handler {self.__class__.__name__} with parameters {parameters}"
        )
        self._db_connection.execute(self._query_one, parameters)
        stop = time.time()
        self._debug(f"End query for handler {self.__class__.__name__} ({stop - start})")

        columns = [col[0] for col in self._db_connection.description]
        row = self._db_connection.fetchone()

        return dict(zip(columns, row)) if row else None

    def import_many(self, ecolo_id: str | None):
        """
        Public entry point method to fetch a list of models from the Ecoloweb database based on its foreign key
        """
        if self._query_many is None:
            raise NotImplementedError

        if ecolo_id is not None:
            iterator = QueryResultIterator(
                self._query_many,
                self._db_connection,
                self.build_query_parameters(ecolo_id),
            )

            for result in iterator:
                self.process_result(result)
