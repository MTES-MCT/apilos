from conventions.models import Convention
from programmes.models import Lot

def conventions_index(user, infilter={}):
    infilter.update(user.convention_filter())
    return Convention.objects.prefetch_related('programme').filter(**infilter)


def conventions_step1(user, infilter={}):
    infilter.update(user.programme_filter())
    return Lot.objects.prefetch_related('programme').filter(**infilter).order_by('programme__nom', 'financement')
