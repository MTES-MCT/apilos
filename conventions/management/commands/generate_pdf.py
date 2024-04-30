import subprocess

from django.core.management.base import BaseCommand

from conventions.models import Convention
from conventions.services.convention_generator import (
    generate_convention_doc,
    get_tmp_local_path,
    run_pdf_convert_cmd,
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--convention-uuid",
            help="Convention UUID",
            required=True,
        )

    def handle(self, *args, **options):
        convention_uuid = options["convention_uuid"]

        try:
            convention = Convention.objects.get(uuid=convention_uuid)
        except Convention.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Convention with UUID {convention_uuid} does not exist"
                )
            )
            return

        local_path = get_tmp_local_path()
        local_docx_path = local_path / f"convention_{convention_uuid}.docx"
        local_pdf_path = local_path / f"convention_{convention_uuid}.pdf"

        doc = generate_convention_doc(convention=convention)
        doc.save(filename=local_docx_path)
        self.stdout.write(self.style.SUCCESS(f"Generated DOCX file: {local_docx_path}"))

        try:
            result = run_pdf_convert_cmd(
                src_docx_path=local_docx_path,
                dst_pdf_path=local_pdf_path,
            )

            if result.returncode != 0:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error while converting DOCX to PDF: {result.stderr}"
                    )
                )
                return

            self.stdout.write(
                self.style.SUCCESS(f"Generated PDF file: {local_pdf_path}")
            )

        except subprocess.CalledProcessError as err:
            self.stdout.write(self.style.ERROR(f"Error: {err}"))
