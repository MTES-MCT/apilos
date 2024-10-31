import datetime

from django.core.management.base import BaseCommand

from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from conventions.services.avenants import _get_last_avenant
from conventions.services.recapitulatif import (
    convention_denonciation_validate,
    convention_resiliation_validate,
)
from users.models import User

# Exemple d'utilisation :
# python manage.py denonciation_batch --numeros "1" "2" "3" --dates "01/12/2024 "02/12/2024" "03/12/2024"
#


class Command(BaseCommand):
    counter_success = 0
    counter_avenants = 0
    numeros_not_found = []

    def add_arguments(self, parser):

        parser.add_argument(
            "--mode",
            help="Choix entre la dénonciation ou la résiliation du batch",
            choices=["denonciation", "resiliation"],
            default="denonciation",
        )

        parser.add_argument(
            "--numeros",
            help="Numéros des conventions à dénoncer",
            action="store",
            nargs="*",
            default=[],
        )

        parser.add_argument(
            "--dates",
            help="Dates de dénonciation",
            action="store",
            nargs="*",
            default=[],
        )

    def convention_update(self, numero, date, mode: str):
        if mode == "resiliation":
            target_statut = ConventionStatut.RESILIEE.label
            db_field_date_name = "date_resiliation"
        else:
            target_statut = ConventionStatut.DENONCEE.label
            db_field_date_name = "date_denonciation"
        date_python = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        user = User.objects.filter(email="sylvain.delabye@beta.gouv.fr").first()
        qs = Convention.objects.filter(numero=numero)
        if qs.count() == 0:
            self.stdout.write(self.style.WARNING(f"Convention {numero} not found."))
            self.numeros_not_found.append(numero)
            return
        elif qs.count() > 1:
            self.stdout.write(
                self.style.WARNING(
                    f"Several conventions found for {numero}. Updating status anyway."
                )
            )

        for convention in qs:
            if convention.statut == target_statut:
                self.stdout.write(
                    self.style.WARNING(
                        f"Convention {numero} already in statut {target_statut}"
                    )
                )
                return
            last_avenant = _get_last_avenant(convention)
            new_avenant = last_avenant.clone(user, convention_origin=convention)
            if mode == "resiliation":
                new_avenant.date_resiliation = date_python
            else:
                new_avenant.date_denonciation = date_python
            new_avenant.numero = new_avenant.get_default_convention_number()
            new_avenant.save()
            if mode == "resiliation":
                convention_resiliation_validate(convention_uuid=new_avenant.uuid)
            else:
                convention_denonciation_validate(convention_uuid=new_avenant.uuid)

        self.counter_success += 1
        self.stdout.write(
            f"Updated convention {numero} with statut "
            f"{target_statut} and {db_field_date_name} {date_python}"
        )

    def handle(self, *args, **options):

        mode = options["mode"]
        numeros = options["numeros"]
        dates = options["dates"]

        if len(numeros) != len(dates):
            self.stdout.write(
                self.style.ERROR(
                    f"There must be the same number of numeros ({len(numeros)}) and dates ({len(dates)})"
                )
            )
            return

        for i in range(len(numeros)):
            self.convention_update(numero=numeros[i], date=dates[i], mode=mode)

        self.stdout.write("===== EXECUTION SUMMARY ====== ")
        self.stdout.write(f"Conventions updated: {self.counter_success}")
        self.stdout.write(f"Conventions not found: {len(self.numeros_not_found)}")
        if len(self.numeros_not_found) > 0:
            self.stdout.write("===== NUMEROS NOT FOUND ====== ")
        for numero in self.numeros_not_found:
            self.stdout.write(numero)
