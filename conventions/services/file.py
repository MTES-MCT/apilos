import datetime

import dramatiq
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from conventions.models import Convention, ConventionStatut, PieceJointe
from core.storage import client
from upload.services import UploadService


class ConventionFileService:

    @classmethod
    def upload_convention_file(cls, convention: Convention, file: File):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{now}_convention_{convention.uuid}_signed.pdf"
        upload_service = UploadService(
            convention_dirpath=f"conventions/{convention.uuid}/convention_docs",
            filename=filename,
        )
        upload_service.upload_file(file)

        convention.statut = ConventionStatut.SIGNEE
        convention.nom_fichier_signe = filename
        convention.televersement_convention_signee_le = timezone.now()
        convention.save()

    @classmethod
    def promote_piece_jointe(cls, piece_jointe: PieceJointe) -> bool:
        file = client.get_object(settings.AWS_ECOLOWEB_BUCKET_NAME, f'piecesJointes/{piece_jointe.fichier}')
        if file is None:
            return False

        cls.upload_convention_file(piece_jointe.convention, file)
        return True

    @staticmethod
    @dramatiq.actor
    def promote_piece_jointe_async(pk: int):
        piece_jointe = PieceJointe.objects.get(pk)
        ConventionFileService.promote_piece_jointe(piece_jointe)