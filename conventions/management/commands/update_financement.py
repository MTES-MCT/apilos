from django.core.management.base import BaseCommand

from conventions.models.convention import Convention

# Exemple d'utilisation :
# python manage.py update_financement --numeros "1" "2" "3" --financement PLAI
#


class Command(BaseCommand):
    counter_success = 0
    numeros_not_found = []

    def add_arguments(self, parser):

        parser.add_argument(
            "--financement",
            help="Choix entre SANS_FINANCEMENT, PLAI, PLS, PLUS",
            choices=["SANS_FINANCEMENT", "PLAI", "PLS", "PLUS", "PALULOS"],
        )

        parser.add_argument(
            "--numeros",
            help="Numéros des conventions à modifier",
            action="store",
            nargs="*",
            default=[],
        )

    def financement_update(self, numero, new_financement):
        qs = Convention.objects.filter(numero=numero)
        if qs.count() == 0:
            self.stdout.write(self.style.WARNING(f"Convention {numero} not found."))
            self.numeros_not_found.append(numero)
            return
        elif qs.count() > 1:
            self.stdout.write(
                self.style.WARNING(
                    f"Several conventions found for {numero}. Updating financement anyway."
                )
            )

        for convention in qs:
            if (
                convention.financement == new_financement
                and convention.lot.financement == new_financement
            ):
                self.stdout.write(
                    self.style.WARNING(
                        f"Convention {numero} already in financement {new_financement}"
                    )
                )
                return
            convention.financement = new_financement
            convention.lot.financement = new_financement
            convention.save()
            convention.lot.save()
            for avenant in convention.avenants.all():
                avenant.financement = new_financement
                avenant.lot.financement = new_financement
                avenant.save()
                avenant.lot.save()

        self.counter_success += 1
        self.stdout.write(
            f"Updated convention {numero} with financement {new_financement}"
        )

    def handle(self, *args, **options):

        financement = options["financement"]
        numeros = options["numeros"]

        for numero in numeros:
            self.financement_update(numero=numero, new_financement=financement)

        self.stdout.write("===== EXECUTION SUMMARY ====== ")
        self.stdout.write(f"Conventions updated: {self.counter_success}")
        self.stdout.write(f"Conventions not found: {len(self.numeros_not_found)}")
        if len(self.numeros_not_found) > 0:
            self.stdout.write("===== NUMEROS NOT FOUND ====== ")
        for numero in self.numeros_not_found:
            self.stdout.write(numero)
