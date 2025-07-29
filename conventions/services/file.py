import datetime
import logging
from enum import Enum

from django.conf import settings
from django.core.files import File

from conventions.models import Convention, ConventionStatut, PieceJointe
from core.storage import client
from upload.services import UploadService

from .utils import convention_upload_filename, document_publication_upload_filename

logger = logging.getLogger(__name__)


class FileType(Enum):
    CONVENTION = "Convention"
    PUBLICATION = "Publication"


class ConventionFileService:
    @classmethod
    def upload_convention_file(
        cls, convention: Convention, file: File, update_statut: bool = True
    ):
        upload_filename = convention_upload_filename(convention)

        upload_service = UploadService(
            convention_dirpath=f"conventions/{convention.uuid}/convention_docs",
            filename=upload_filename,
        )
        upload_service.upload_file(file)

        if update_statut and not convention.statut == ConventionStatut.DENONCEE.label:
            convention.statut = ConventionStatut.SIGNEE.label
            convention.televersement_convention_signee_le = datetime.date.today()

        convention.nom_fichier_signe = upload_filename
        convention.save()

    @classmethod
    def upload_publication_file(
        cls, convention: Convention, file: File, update_statut: bool = True
    ):
        upload_filename = document_publication_upload_filename(convention)

        upload_service = UploadService(
            convention_dirpath=f"spf/{convention.uuid}/publication",
            filename=upload_filename,
        )
        upload_service.upload_file(file)

        if (
            update_statut
            and convention.statut == ConventionStatut.PUBLICATION_EN_COUR.label
        ):
            convention.statut = ConventionStatut.PUBLIE.label
            convention.date_publication_spf = datetime.date.today()

        convention.nom_fichier_publication_spf = upload_filename
        convention.save()

    @classmethod
    def upload_file(
        cls,
        convention: Convention,
        file: File,
        as_type: FileType,
        update_statut: bool = True,
    ):
        if as_type == FileType.PUBLICATION:
            cls.upload_publication_file(convention, file, update_statut)
            return

        cls.upload_convention_file(convention, file, update_statut)

    @classmethod
    def promote_piece_jointe(cls, piece_jointe: PieceJointe):
        try:
            file = client.get_object(
                settings.AWS_ECOLOWEB_BUCKET_NAME,
                f"piecesJointes/{piece_jointe.fichier}",
            )
            if file is not None:
                # TODO mark piece jointe as missing
                cls.upload_convention_file(piece_jointe.convention, file, False)
        except FileNotFoundError as err:
            logger.warning(err, exc_info=True)
