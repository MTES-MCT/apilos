from conventions.models import Convention
from programmes.models import Lot

def conventions_index(request, infilter={}):
    infilter.update(request.user.convention_filter())
    conventions = Convention.objects.prefetch_related('programme').filter(**infilter)
    return conventions


def conventions_step1(request, infilter={}):
    infilter.update(request.user.programme_filter())
    return Lot.objects.prefetch_related('programme').filter(**infilter).order_by('programme__nom', 'financement')
