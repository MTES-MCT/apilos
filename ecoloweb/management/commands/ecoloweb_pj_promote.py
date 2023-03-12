from django.core.management import BaseCommand

from conventions.models import Convention, PieceJointeType
from conventions.services.file import ConventionFileService
from ecoloweb.models import EcoloReference


class Command(BaseCommand):
    help = "Process piece jointe ot promoted automatically"

    def add_arguments(self, parser):
        parser.add_argument(
            "nb_conventions",
            type=int,
            default=50,
            help="Nb of conventions to process",
        )

    def handle(self, *args, **options):
        nb_conventions = options["nb_conventions"]

        conventions = Convention.objects.filter(
            televersement_convention_signee_le__isnull=True,
            id__in=EcoloReference.objects.filter().only("apilos_id").all(),
        )[:nb_conventions]

        for convention in conventions:
            piece_jointe = None
            if convention.is_avenant():
                # Le PDF assigné à un avenant est celui de la n-ième pièce jointe par ordre de création de type AVENANT,
                # avec n le numéro de l'avenant
                numero = int(convention.numero)

                if numero >= 1:
                    try:
                        piece_jointe = convention.pieces_jointes.filter(
                            type=PieceJointeType.AVENANT
                        ).order_by("cree_le")[numero - 1]
                    except IndexError:
                        piece_jointe = None
            else:
                # Le PDF assigné à une convention est celui de la pièce jointe la plus récente de type CONVENTION
                piece_jointe = (
                    convention.pieces_jointes.filter(type=PieceJointeType.CONVENTION)
                    .order_by("-cree_le")
                    .first()
                )

            ConventionFileService.promote_piece_jointe(piece_jointe)
            convention.promote_piece_jointe(False)
