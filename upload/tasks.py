from celery import shared_task
import subprocess
from upload.models import UploadedFile, UploadedFileSerializer


@shared_task()
def scan_uploaded_files(files_ids):
    # refresh the database on demand before the scan starts
    subprocess.run("freshclam", shell=True, check=True)
    files = UploadedFile.objects.filter(id__in=files_ids)
    paths = [file.filepath for file in files]
    for path in paths:
        print("SCAN", path)
        subprocess.run(["clamscan", path], shell=True, check=True)
