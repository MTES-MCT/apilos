from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # pylint: disable=R0912,R0914,R0915
    def handle(self, *args, **options):

        print("Salut Ambroise !!!")
