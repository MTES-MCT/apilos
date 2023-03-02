import datetime
import logging

from django.conf import settings
from django.core.files import File
from django.utils import timezone

from conventions.models import Convention, ConventionStatut, PieceJointe
from core.storage import client
from upload.services import UploadService

logger = logging.getLogger(__name__)


class ConventionFileService:
    @classmethod
    def upload_convention_file(
        cls, convention: Convention, file: File, update_statut: bool = True
    ):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{now}_convention_{convention.uuid}_signed.pdf"
        upload_service = UploadService(
            convention_dirpath=f"conventions/{convention.uuid}/convention_docs",
            filename=filename,
        )
        upload_service.upload_file(file)

        if update_statut:
            convention.statut = ConventionStatut.SIGNEE
            convention.televersement_convention_signee_le = timezone.now()

        convention.nom_fichier_signe = filename
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
        except FileNotFoundError as fnfe:
            logger.warning(fnfe)
