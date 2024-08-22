import json

import factory

from core.tests.factories import BaseFactory
from upload.models import UploadedFile


class UploadedFileFactory(BaseFactory):
    class Meta:
        model = UploadedFile

    filename = factory.Faker("file_name")
    size = factory.Faker("pyint")
    content_type = factory.Faker("mime_type")


FILES = [
    {
        "thumbnail": "data:image/png;base64,BLAHBLAH==",
        "size": "31185",
        "filename": "acquereur1.png",
        "content_type": "image/png",
    },
    {
        "thumbnail": "data:image/png;base64,BLIHBLIH==",
        "size": "69076",
        "filename": "acquereur2.png",
        "content_type": "image/png",
    },
]


def create_upload_files() -> str:
    files_and_text = {"text": "this is a test", "files": {}}
    for file in FILES:
        uploaded_file = UploadedFileFactory(
            filename=file["filename"],
            size=file["size"],
            content_type=file["content_type"],
        )
        files_and_text["files"][str(uploaded_file.uuid)] = {
            "uuid": str(uploaded_file.uuid),
            **file,
        }
    return json.dumps(files_and_text)


class UploadFactoryMixin(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True
        skip_postgeneration_save = True

    @factory.post_generation
    def make_upload_on_fields(instance, create, extracted, **kwargs):  # noqa: N805
        if extracted:
            for field_name in extracted:
                setattr(instance, field_name, create_upload_files())
            if create:
                instance.save()
