import csv

from django.core.management.base import BaseCommand
from django.db.models import Count

from conventions.models import Convention
from conventions.models.choices import ConventionStatut


def data_to_csv(data, header, filename):

    # Open (or create) your CSV file
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        # Write the header
        writer.writerow(header)

        # Write the data
        for row in data:
            writer.writerow(row)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            help="Dry run",
            action="store_true",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        deletions = []

        programme_financement_duplicates = (
            Convention.objects.exclude(statut=ConventionStatut.ANNULEE.label)
            .values("programme_id", "financement", "lot__type_habitat")
            .annotate(lot_count=Count("id"))
            .filter(lot_count__gt=1)
        )
        count = 0
        count_delete = 0
        for duplicate in programme_financement_duplicates:
            conventions = (
                Convention.objects.filter(
                    programme_id=duplicate["programme_id"],
                    financement=duplicate["financement"],
                )
                .exclude(statut=ConventionStatut.ANNULEE.label)
                .prefetch_related("cree_par")
            )

            convention_count = conventions.count()
            convention_status = [convention.statut for convention in conventions]
            lot_count = len({convention.lot_id for convention in conventions})

            not_signed_conventions = [
                c for c in conventions if c.statut != ConventionStatut.SIGNEE.label
            ]

            # Not all conventions are signed and there is 1 lot by convention
            if not_signed_conventions and lot_count == convention_count:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{conventions[0].programme.numero_galion} : {convention_count}"
                        f" convention(s) with status {', '.join(convention_status)}"
                    )
                )
                count += 1
                inside_count = 1
                for duplicate in conventions:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{inside_count} : {duplicate} - {duplicate.statut} - "
                            f"{duplicate.cree_le} - "
                            f"{duplicate.cree_par.email if duplicate.cree_par else '-'}"
                        )
                    )
                    inside_count += 1
                option = input(
                    "Which convention do you want to delete (type a number) ? "
                )
                self.stdout.write(self.style.SUCCESS(f"choosed option : {option}"))
                if (option.isdigit() and int(option) > len(conventions)) or (
                    not option.isdigit()
                ):
                    self.stdout.write(self.style.ERROR("No deletion"))
                    continue
                selected_convention = conventions[int(option) - 1]

                if not dry_run:
                    to_delete = input(
                        f"Are you sure you want to delete {selected_convention} - {selected_convention.statut} ? (y/N)"
                    )
                    if to_delete != "y":
                        self.stdout.write(
                            self.style.ERROR("Not confirmed : no deletion")
                        )
                        continue

                deletions.append(
                    [
                        f"{selected_convention.lot.id}",
                        f"{selected_convention.programme.numero_galion}",
                        f"{selected_convention}",
                        f"{selected_convention.cree_le}",
                        f"{selected_convention.cree_par.email if duplicate.cree_par else '-'}",
                    ]
                )
                if not dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Removing {selected_convention} - {selected_convention.statut}"
                        )
                    )
                    selected_convention.delete()
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Would be removed {selected_convention} - {selected_convention.statut}"
                        )
                    )

                count_delete += 1
                self.stdout.write(self.style.SUCCESS(deletions))

        self.stdout.write(
            self.style.SUCCESS(f"Found {count} conventions with duplicated lots")
        )
        self.stdout.write(self.style.SUCCESS(f"{count_delete} conventions deleted"))
        data_to_csv(
            deletions,
            ["lot id", "programme", "convention", "created at", "created by"],
            "output.csv",
        )
