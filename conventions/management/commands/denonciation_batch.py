import datetime

from django.core.management.base import BaseCommand

from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from conventions.services.avenants import _get_last_avenant
from conventions.services.recapitulatif import convention_denonciation_validate
from users.models import User

numeros = [
    "34/2/10-2007/2002-846/3755",
    "34/2/11-2007/2002-846/3761",
    "34/2/4-2007/2002-846/3544",
    "34/3/7-2004/80-429/2935",
    "34/3/10-2007/2002-846/3864",
    "34/3/12-2007/2002-846/3661",
    "34/2/1-2008/2002-846/3509",
    "34/2/10-2007/2002-846/3759",
    "34/2/3-2008/2002-846/3802",
    "34/2/12-2006/2002-846/3224",
    "34/3/02.2002/80.429/2306",
    "34/2/12-2007/2002-846/3788",
    "34/2/3-2008/2002-846/3967",
    "34/2/4-2007/2002-846/3572",
    "34/3/10-2007/2002-846/3859",
    "34/3/12-2007/2002-846/3662",
    "34/2/11-2007/2002-846/3898",
    "34/2/11-2007/2002-846/3899",
    "34/2/2-2008/2002-846/3959",
    "34/3/10-2007/2002-846/3855",
    "34/2/7-2008/2002-846/3904",
    "34/2/2-2002/80-429/2562",
    "34/2/9-2008/2002-846/4182",
    "34/2/4-2007/2002-846/3545",
    "34/2/2-2008/2002-846/3958",
    "34/2/10-2007/2002-846/3754",
    "34/2/11-2007/2002-846/3767",
    "34/2/1-2008/2002-846/3832",
    "34/2/1-2008/2002-846/3835",
    "34/2/2-2008/2002-846/3948",
    "34/2/7-2008/2002-846/4070",
    "34/2/2-2008/2002-846/3953",
    "34/3/10-2007/2002-846/3865",
    "34/3/11-2007/2002-846/3871",
    "34/3/10-2007/2002-846/3866",
    "34/3/9-1982/79-444/0173",
    "34/2/2-2008/2002-846/3957",
    "34/2/11-2007/2002-846/3773",
    "34/2/4-2007/2002-846/3568",
    "34/2/7-2008/2002-846/3905",
    "34/3/5-2008/2002-846/3875",
    "34/2/1-2008/2002-846/3513",
    "34/2/10-2007/2002-846/3756",
    "34/2/4-2007/2002-846/3552",
    "34/2/10-2006/2002-846/3511",
    "34/2/12-2007/2002-846/3829",
    "34/2/9-2008/2002-846/4253",
    "34/2/1-2008/2002-846/3837",
    "34/3/3-1998/80-429/2032",
    "34/3/3-1990/80-429/0807",
    "34/2/4-2007/2002-846/3549",
]

dates = [
    "21/12/2020",
    "29/12/2020",
    "18/01/2021",
    "16/04/2021",
    "16/12/2021",
    "01/12/2021",
    "29/12/2021",
    "20/01/2022",
    "28/03/2022",
    "02/06/2022",
    "29/09/2022",
    "29/09/2022",
    "17/08/2022",
    "22/07/2022",
    "24/10/2022",
    "10/10/2022",
    "04/11/2022",
    "04/11/2022",
    "04/11/2022",
    "10/11/2022",
    "07/12/2022",
    "29/11/2022",
    "28/11/2022",
    "18/11/2022",
    "14/12/2022",
    "23/11/2022",
    "17/10/2022",
    "21/11/2022",
    "21/11/2022",
    "13/12/2022",
    "17/11/2022",
    "15/12/2022",
    "14/12/2022",
    "23/12/2022",
    "23/12/2022",
    "29/12/2022",
    "24/10/2022",
    "29/12/2022",
    "29/12/2022",
    "24/09/2019",
    "12/09/2018",
    "19/12/2022",
    "21/12/2022",
    "22/12/2022",
    "06/12/2022",
    "01/12/2022",
    "23/12/2022",
    "17/11/2022",
    "29/11/2008",
    "24/11/2022",
    "21/12/2022",
]


class Command(BaseCommand):
    counter_success = 0
    counter_avenants = 0
    numeros_not_found = []

    def convention_denonciation(self, numero, date):
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
            last_avenant = _get_last_avenant(convention)
            avenant_denonciation = convention.clone(
                user, convention_origin=last_avenant
            )
            avenant_denonciation.date_denonciation = date_python
            avenant_denonciation.numero = (
                avenant_denonciation.get_default_convention_number()
            )
            avenant_denonciation.save()
            convention_denonciation_validate(convention_uuid=avenant_denonciation.uuid)

        self.counter_success += 1
        self.stdout.write(
            f"Updated convention {numero} with statut "
            f"{ConventionStatut.DENONCEE.label} and date_denonciation {date_python}"
        )

    def handle(self, *args, **options):
        assert len(numeros) == len(dates)

        for i in range(len(numeros)):
            self.convention_denonciation(numero=numeros[i], date=dates[i])

        self.stdout.write("===== EXECUTION SUMMARY ====== ")
        self.stdout.write(f"Conventions updated: {self.counter_success}")
        self.stdout.write(f"Conventions not found: {len(self.numeros_not_found)}")
        if len(self.numeros_not_found) > 0:
            self.stdout.write("===== NUMEROS NOT FOUND ====== ")
        for numero in self.numeros_not_found:
            self.stdout.write(numero)
