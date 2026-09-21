import pickle

from django.core.management.base import BaseCommand
from django.db import connection
from django_cryptography.utils.crypto import FernetBytes


class Command(BaseCommand):
    help = "Fixes corrupted explorer_databaseconnection encrypted fields "
    "after a cryptography update or SECRET_KEY change."

    def handle(self, *args, **options):
        # Generate an encrypted empty string using the current SECRET_KEY
        fernet = FernetBytes()
        encrypted_empty = fernet.encrypt(pickle.dumps(""))

        with connection.cursor() as cursor:
            # Re-encrypt 'host' with the new key (host cannot be NULL)
            cursor.execute(
                "UPDATE explorer_databaseconnection SET host = %s", [encrypted_empty]
            )
            # user, password, and port can safely be set to NULL
            cursor.execute(
                'UPDATE explorer_databaseconnection SET "user" = NULL, password = NULL, port = NULL'
            )

            rowcount = cursor.rowcount

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully reset {rowcount} corrupted database connections."
            )
        )
