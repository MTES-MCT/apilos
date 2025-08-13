from django.core.management.base import BaseCommand

from instructeurs.models import Administration


class Command(BaseCommand):
    help = "Foo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            help="Verbose output",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--dry-run",
            help="Dry run",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options):
        verbose = options["verbose"]
        dry_run = options["dry_run"]

        ddt = Administration.objects.filter(code__startswith="DD").exclude(
            code__startswith="DDI"
        )
        self.stdout.write(self.style.SUCCESS(f"## {ddt.count()} DDT"))
        self.stdout.write(self.style.SUCCESS(""))
        if verbose:
            for d in ddt.order_by("code"):
                self.stdout.write(self.style.SUCCESS(f"{d.code} - {d.nom}"))
            self.stdout.write(self.style.SUCCESS(""))
        ddi = Administration.objects.filter(code__startswith="DDI")
        self.stdout.write(self.style.SUCCESS(f"\n## {ddi.count()} DDI\n"))
        self.stdout.write(self.style.SUCCESS(""))
        if verbose:
            for d in ddi.order_by("code"):
                self.stdout.write(self.style.SUCCESS(f"{d.code} - {d.nom}"))
        ddi_codes = [d.code for d in ddi]
        ddi_by_code = {d.code: d for d in ddi}
        ddt_ddi = {}
        for dd in ddt:
            ddi_code = dd.code.replace("DD", "DDI")
            if ddi_code in ddi_codes:
                ddt_ddi[dd.code] = ddi_by_code[ddi_code]
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"{dd.code} - {dd.nom} doesn't have a DDI equivalence"
                    )
                )
        nb_conventions_total = 0
        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("## Détails par DDT"))
        self.stdout.write(self.style.SUCCESS(""))
        for d in ddt.order_by("code"):
            nb_conventions_ddt = 0
            conventions = []
            self.stdout.write(self.style.SUCCESS(""))
            self.stdout.write(self.style.SUCCESS(f"### {d.code} - {d.nom}"))
            self.stdout.write(self.style.SUCCESS(""))
            if nb_programme := d.programmes.all().count():
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{d.code} - {d.nom} : {nb_programme} programmes"
                    )
                )
                nb_users = len(list(set([r.user for r in d.roles.all()])))
                if nb_users > 1:
                    self.stdout.write(
                        self.style.NOTICE(f"{d.code} - {d.nom} : {nb_users} users")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"{d.code} - {d.nom} : {nb_users} users")
                    )
            for p in d.programmes.all():
                for c in p.conventions.all():
                    nb_conventions_ddt += 1
                    conventions.append(c)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{d.code} - {d.nom} : {nb_conventions_ddt} conventions"
                )
            )
            if verbose:
                self.stdout.write(self.style.SUCCESS(""))
                self.stdout.write(self.style.SUCCESS("#### Conventions"))
                self.stdout.write(self.style.SUCCESS(""))
                for c in conventions:
                    self.stdout.write(self.style.SUCCESS(f"{c} ({c.uuid})"))
            nb_conventions_total += nb_conventions_ddt
        self.stdout.write(self.style.SUCCESS(f"{nb_conventions_total} conventions"))

        self.stdout.write(self.style.WARNING(""))
        self.stdout.write(self.style.WARNING("Début de ré-attribution"))
        for d in ddt.order_by("code"):
            self.stdout.write(self.style.WARNING(""))
            self.stdout.write(
                self.style.WARNING(
                    f"Début de ré-attribution pour la DDT {d.code} - {d.nom} vers"
                    f" {ddt_ddi[d.code].code} ({ddt_ddi[d.code].nom})"
                )
            )
            self.stdout.write(self.style.WARNING(""))
            for p in d.programmes.all():
                if verbose:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Ré-attribution de {p} de {d.code} vers {ddt_ddi[d.code].code}"
                        )
                    )
                if not dry_run:
                    p.administration_id = ddt_ddi[d.code].id
                    p.save()
            if d.programmes.all().count() != 0 and not dry_run:
                raise Exception(
                    f"La DDT {d.code} - {d.nom} a plusieurs programmes après"
                    f" ré-attribution : {d.programmes.all()}"
                )
            self.stdout.write(self.style.SUCCESS(""))
            self.stdout.write(
                self.style.SUCCESS(f"Suppression de la DDT {d.code} - {d.nom}")
            )
            if not dry_run:
                d.delete()
