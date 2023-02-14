import cProfile
import pstats


from django.core.management.base import BaseCommand

from conventions.models import Convention
from conventions.services import convention_generator


class Command(BaseCommand):
    # pylint: disable=R0912,R0914,R0915
    def handle(self, *args, **options):
        convention_uuid = input(
            "Quel est l'identifiant UUID de la convention à profiler ? "
        )

        convention = Convention.objects.get(uuid=convention_uuid)
        with cProfile.Profile() as pr:

            convention_generator.generate_convention_doc(convention)
            stats = pstats.Stats(pr).sort_stats(pstats.SortKey.CUMULATIVE)
            # stats.print_stats("convention_generator", 0.1)
            stats.print_stats()
