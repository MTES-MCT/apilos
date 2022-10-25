from .handlers import ModelImportHandler

from instructeurs.models import Administration


class AdministrationImportHandler(ModelImportHandler):
    model = Administration
    sql_template = 'resources/sql/administrations.sql'
