from django.core.management.base import BaseCommand, CommandError

from bailleurs.models import Bailleur
from programmes.models.models import Programme


class Command(BaseCommand):
    help = "Transfert all Programmes from one Bailleur (old) into another Bailleur (new) using SIREN or SIRET."

    def add_arguments(self, parser):
        parser.add_argument(
            "--old-bailleur",
            type=str,
            required=True,
            help="SIREN (9 digits) or SIRET (14 digits) of the old Bailleur",
        )
        parser.add_argument(
            "--new-bailleur",
            type=str,
            required=True,
            help="SIREN (9 digits) or SIRET (14 digits) of the new Bailleur",
        )

    def handle(self, *args, **options):
        old_id = options["old_bailleur"]
        new_id = options["new_bailleur"]

        def get_bailleur(identifier: str):
            if len(identifier) == 14:  # SIRET
                return Bailleur.objects.filter(siret=identifier).first()
            elif len(identifier) == 9:  # SIREN
                return Bailleur.objects.filter(siren=identifier).first()
            else:
                raise CommandError(
                    f"Identifier {identifier} is not a valid SIREN (9) or SIRET (14)"
                )

        old_bailleur = get_bailleur(old_id)
        if not old_bailleur:
            raise CommandError(f"No Bailleur found for identifier {old_id}")

        new_bailleur = get_bailleur(new_id)
        if not new_bailleur:
            raise CommandError(f"No Bailleur found for identifier {new_id}")

        programmes_to_update = Programme.objects.filter(bailleur=old_bailleur)
        count_old = programmes_to_update.count()

        if count_old == 0:
            self.stdout.write(
                self.style.WARNING(f"No Programmes found for {old_bailleur}")
            )
            return

        updated = programmes_to_update.update(bailleur=new_bailleur)

        self.stdout.write(
            self.style.SUCCESS(
                f"Moved {updated} Programmes from {old_bailleur} to {new_bailleur}"
            )
        )
