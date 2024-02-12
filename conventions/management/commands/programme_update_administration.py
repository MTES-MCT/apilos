from django.core.management.base import BaseCommand

from instructeurs.models import Administration
from programmes.models import Programme


class Command(BaseCommand):
    def handle(self, *args, **options):

        programme_uuid = input("Quel est l'identifiant UUID du programme à modifier ? ")
        programme = Programme.objects.get(uuid=programme_uuid)
        self.stdout.write(
            f"le programme `{programme_uuid}` : `{programme}` va être modifié"
        )

        administration_code = input(
            "Quel est le code de l'administration à laquelle le programme doit être rattacher ? "
        )
        administration = Administration.objects.get(code=administration_code)
        self.stdout.write(
            f"le programme `{programme}` va être attribué à l'administration"
            + f" `{administration}` de code `{administration_code}`"
        )

        go = input("Modifier l'administration du programme (Non/oui)?")

        if go.lower() == "oui":
            programme.administration = administration
            programme.save()
            self.stdout.write(
                f"l'administration du programme `{programme}` a été mise à "
                + f"jour avec l'administration de code `{administration_code}`"
            )

        self.stdout.write(
            f"le programme `{programme}` va être attribué à l'administration"
            + f" `{administration}` de code `{administration_code}`"
        )
