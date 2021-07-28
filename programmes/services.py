from programmes.models import Programme, Lot

class ProgrammeService():
    @staticmethod
    def all_programmes(user, infilter={}):
        infilter.update(user.programme_filter())
        return Programme.objects.prefetch_related('lot_set').filter(**infilter)

    @staticmethod
    def all_programmes_lots(user, infilter={}):
        infilter.update(user.programme_filter())
        return Lot.objects.prefetch_related('programme').filter(**infilter).order_by('programme__nom', 'financement')
