import errno
import io

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage


class UploadService:
    convention_dirpath: str
    filename: str

    def __init__(
        self,
        convention_dirpath: str = "",
        filename: str = "",
    ):
        self.convention_dirpath = convention_dirpath
        self.filename = filename

    def copy_local_file(self, src_path: str) -> None:
        with open(src_path, "rb") as src_file:
            self.upload_file(File(src_file))

    def upload_file(self, file: File) -> None:
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

        for chunk in file.chunks():
            destination.write(chunk)

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

    def get_file(self, filepath=None) -> File:
        filepath = filepath or self.path
        return default_storage.open(
            filepath,
            "rb",
        )

    def get_io_file(self, filepath=None) -> io.BytesIO:
        filepath = filepath or self.path
        content = b""
        with default_storage.open(filepath, "rb") as file:
            content = file.read()
        return io.BytesIO(content)

    @property
    def path(self):
        return f"{self.convention_dirpath}/{self.filename}"
