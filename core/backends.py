from django_cas_ng.backends import CASBackend


class CerbereCASBackend(CASBackend):
    def user_can_authenticate(self, user):
        return True
