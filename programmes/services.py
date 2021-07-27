from programmes.models import Programme

class ProgrammeService():
    @staticmethod
    def all_programmes(user, infilter={}):
        if user.is_bailleur():
            infilter = {} # add filter list
        return Programme.objects.filter(**infilter)
