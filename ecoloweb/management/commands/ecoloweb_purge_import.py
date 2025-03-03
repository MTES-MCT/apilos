import sys

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connections, transaction
from django.db.backends.utils import CursorWrapper


class Command(BaseCommand):
    help = "Purge data from previous Ecoloweb import"

    def add_arguments(self, parser):
        parser.add_argument(
            "departements",
            nargs="+",
            type=str,
            default=[],
            help="Départements on which purge import data",
        )
        parser.add_argument(
            "--keep-models",
            action="store_true",
            help="Keep related APiLos models, do not delete",
        )

    def handle(self, *args, **options):
        if settings.ENVIRONMENT == "production":
            self.stdout.write(
                self.style.NOTICE("This command can't be executed on prod environment")
            )
            sys.exit(1)

        departements = options["departements"]
        keep_models = options["keep_models"]

        connection: CursorWrapper = connections["default"].cursor()

        with transaction.atomic():
            if not keep_models:
                # Purge related ReferenceCadasatrale objects
                connection.execute(
                    """
delete
from programmes_referencecadastrale rc
where exists(
    select *
    from ecoloweb_ecoloreference er
    where
        er.apilos_model = 'programmes.ReferenceCadastrale'
        and er.apilos_id = rc.id
        and departement = any(%s)
)
                    """,
                    [departements],
                )

                # Purge related PieceJointe objects
                connection.execute(
                    """
delete
from conventions_piecejointe pj
where exists(
    select *
    from ecoloweb_ecoloreference er
    where
        er.apilos_model = 'conventions.PieceJointe'
        and er.apilos_id = pj.id
        and departement = any(%s)
)
                    """,
                    [departements],
                )

                # Purge related Logement objects
                connection.execute(
                    """
delete
from programmes_logement lg
where exists(
    select *
    from ecoloweb_ecoloreference er
    where
        er.apilos_model = 'programmes.Logement'
        and er.apilos_id = lg.id
        and departement = any(%s)
)
                    """,
                    [departements],
                )

                # Purge related Lot objects
                connection.execute(
                    """
delete
from programmes_lot l
where exists(
    select *
    from ecoloweb_ecoloreference er
    where
        er.apilos_model = 'programmes.Lot'
        and er.apilos_id = l.id
        and departement = any(%s)
)
                    """,
                    [departements],
                )

                # Purge related AvenantType objects
                connection.execute(
                    """
delete
from conventions_convention_avenant_types cat
where exists(
    select *
    from ecoloweb_ecoloreference er
    where
        er.apilos_model = 'conventions.Convention'
        and er.apilos_id = cat.convention_id
        and departement = any(%s)
)
                    """,
                    [departements],
                )

                # Purge related Comments objects
                connection.execute(
                    """
delete
from comments_comment cc
where exists(
    select *
    from ecoloweb_ecoloreference er
    where
        er.apilos_model = 'conventions.Convention'
        and er.apilos_id = cc.convention_id
        and departement = any(%s)
)
                    """,
                    [departements],
                )

                # Purge related Convention objects
                connection.execute(
                    """
delete
from conventions_convention c
where exists(
    select *
    from ecoloweb_ecoloreference er
    where
        er.apilos_model = 'conventions.Convention'
        and er.apilos_id = c.id
        and departement = any(%s)
)
                    """,
                    [departements],
                )

                # Deleting orphan Programme objects
                connection.execute(
                    """
delete
from programmes_programme p
where not exists(
    select *
    from conventions_convention c
    where
        c.programme_id = p.id
)
            """
                )

            connection.execute(
                "delete from public.ecoloweb_ecoloreference where departement = any(%s)",
                [departements],
            )
