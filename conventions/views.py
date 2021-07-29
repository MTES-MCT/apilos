from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from programmes.models import Lot
from .models import Convention

from . import services
from .forms import ProgrammeSelectionForm

@permission_required('convention.view_convention')
def index(request):
    conventions = services.conventions_index(request)
    return render(request, "conventions/index.html", {'conventions': conventions})

@permission_required('convention.change_convention')
def select_programme_create(request):
    result = services.select_programme_create(request)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step2', args=[result['convention'].uuid]) )
    else:
        return render(request, "conventions/step1.html", {'form': result['form'], 'programmes': result['programmes']})

@permission_required('convention.change_convention')
def select_programme_update(request, convention_uuid):
    result = services.select_programme_update(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step2', args=[result['convention'].uuid]) )
    else:
        return render(request, "conventions/step1.html", {'form': result['form'], 'convention_uuid': result['convention_uuid'], 'programmes': result['programmes']})



@permission_required('convention.change_convention')
def step2(request, convention_uuid):
    print('STEP2')
    result = services.bailleur_update(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step3', args=[result['convention'].uuid]) )
    else:
        print(result['form'])
        return render(request, "conventions/step2.html", {'form': result['form'], 'convention_uuid': result['convention_uuid']})





@permission_required('convention.change_convention')
def step3(request, convention_uuid):
    return render(request, "conventions/step3.html", {'convention_uuid': convention_uuid})

@permission_required('convention.change_convention')
def step4(request, convention_uuid):
    return render(request, "conventions/step4.html", {'convention_uuid': convention_uuid})

@permission_required('convention.change_convention')
def step5(request, convention_uuid):
    return render(request, "conventions/step5.html", {'convention_uuid': convention_uuid})

@permission_required('convention.change_convention')
def step6(request, convention_uuid):
    return render(request, "conventions/step6.html", {'convention_uuid': convention_uuid})

@permission_required('convention.change_convention')
def step7(request, convention_uuid):
    return render(request, "conventions/step7.html", {'convention_uuid': convention_uuid})

@permission_required('convention.change_convention')
def step8(request, convention_uuid):
    return render(request, "conventions/step8.html", {'convention_uuid': convention_uuid})

@permission_required('convention.change_convention')
def step9(request, convention_uuid):
    return render(request, "conventions/step9.html", {'convention_uuid': convention_uuid})

@permission_required('convention.change_convention')
def stepfin(request, convention_uuid):
    return render(request, "conventions/stepfin.html", {'convention_uuid': convention_uuid})
