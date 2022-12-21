import errno

from django.conf import settings
from django.core.files.storage import default_storage


class UploadService:
    # pylint: disable=R0902,R0903,R0913
    convention_dirpath: str
    filename: str

    def __init__(
        self,
        convention_dirpath: str = "",
        filename: str = "",
    ):
        self.convention_dirpath = convention_dirpath
        self.filename = filename

    def upload_file(self, file) -> None:
        if (
            settings.DEFAULT_FILE_STORAGE
            == "django.core.files.storage.FileSystemStorage"
        ):
            convention_dir = settings.MEDIA_ROOT / self.convention_dirpath
            if not convention_dir.exists():
                try:
                    convention_dir.mkdir(parents=True)
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
        destination = default_storage.open(
            f"{self.convention_dirpath}/{self.filename}",
            "bw",
        )

        destination.write(file.read())
        destination.close()

    def upload_file_io(self, file_io) -> None:
        if (
            settings.DEFAULT_FILE_STORAGE
            == "django.core.files.storage.FileSystemStorage"
        ):
            convention_dir = settings.MEDIA_ROOT / self.convention_dirpath
            if not convention_dir.exists():
                try:
                    convention_dir.mkdir(parents=True)
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
        destination = default_storage.open(
            f"{self.convention_dirpath}/{self.filename}",
            "bw",
        )
        destination.write(file_io.getbuffer())
        destination.close()

    def get_file(self, filepath=None):
        if filepath:
            return default_storage.open(
                filepath,
                "rb",
            )
        return default_storage.open(
            f"{self.convention_dirpath}/{self.filename}",
            "rb",
        )
