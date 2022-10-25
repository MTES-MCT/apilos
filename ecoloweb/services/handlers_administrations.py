from .handlers import ModelImporter

from instructeurs.models import Administration


class AdministrationImporter(ModelImporter):
    model = Administration
    sql_template = 'resources/sql/administrations.sql'
