import logging

from django.core.management.base import BaseCommand

from conventions.models import Convention


class Command(BaseCommand):

    def handle(self, *args, **options):
        conventions = (
            Convention.objects.exclude(numero__isnull=True)
            .filter(numero_pour_recherche__isnull=True)
            .exclude(numero="")
            .order_by("id")
        )
        total = conventions.count()
        i = 0
        count = 0
        while convs := conventions[i : i + 1000]:
            logging.warning(f"{i}/{total}")
            for c in convs:
                c.numero_pour_recherche = (
                    c.numero.replace("/", "")
                    .replace("-", "")
                    .replace(" ", "")
                    .replace(".", "")
                )
                count += 1
                c.save()
            i += 1000
        logging.warning(f"Enden : {i}/{count}")
