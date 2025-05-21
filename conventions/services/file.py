import datetime
import logging

from django.conf import settings
from django.core.files import File

from conventions.models import Convention, ConventionStatut, PieceJointe
from core.storage import client
from upload.services import UploadService

from .utils import convention_upload_filename

logger = logging.getLogger(__name__)


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
        upload_service.upload_file(convention, file)

        if update_statut and not convention.statut == ConventionStatut.DENONCEE.label:
            convention.statut = ConventionStatut.SIGNEE.label
            convention.televersement_convention_signee_le = datetime.date.today()

        convention.nom_fichier_signe = upload_filename
        convention.save()

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
