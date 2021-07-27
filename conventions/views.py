from django.contrib.auth.models import Permission
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

from programmes.services import ProgrammeService

programme_service = ProgrammeService()

@login_required
@permission_required('convention.view_convention')
def index(request):
    programmes = programme_service.all_programmes(request.user)
    return render(request, "conventions/index.html", {'programmes':programmes})