from django.contrib.auth.models import Permission
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

from conventions.services import ConventionService

convention_service = ConventionService()

@login_required
@permission_required('convention.view_convention')
def index(request):
    conventions = convention_service.all_conventions(request.user)
    return render(request, "conventions/index.html", {'conventions': conventions})