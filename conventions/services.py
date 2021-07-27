from conventions.models import Convention

class ConventionService():
    @staticmethod
    def all_conventions(user, infilter={}):
        infilter.update(user.convention_filter())
        return Convention.objects.prefetch_related('programme').filter(**infilter)
