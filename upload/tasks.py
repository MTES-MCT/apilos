from celery import shared_task
from django.conf import settings
from pathlib import Path
import subprocess
from upload.models import UploadedFile, UploadedFileSerializer


@shared_task()
def scan_uploaded_files(paths_to_scan):
    # refresh the database on demand before the scan starts
    subprocess.run("freshclam", shell=True, check=True)

    for path in paths_to_scan:
        path = Path(settings.MEDIA_ROOT / path).resolve()
        subprocess.run(f"clamscan {path}", shell=True, check=True)
