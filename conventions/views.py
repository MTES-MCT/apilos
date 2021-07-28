from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from programmes.models import Lot
from .models import Convention

from . import services
from .forms import ProgrammeSelectionForm

@login_required
@permission_required('convention.view_convention')
def index(request):
    conventions = services.conventions_index(request)
    return render(request, "conventions/index.html", {'conventions': conventions})

def step2(request, convention_uuid):
    return render(request, "conventions/step2.html", {'convention_uuid': convention_uuid})

def convention_select_programme_create(request):

    if request.method == 'POST':
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            lot = Lot.objects.get(uuid=form.cleaned_data['lot_uuid'])
            convention = Convention.objects.create(lot=lot, programme_id=lot.programme_id, bailleur_id=lot.bailleur_id, financement=lot.financement)
            convention.save()
            # All is OK -> Next:
            return HttpResponseRedirect(reverse('conventions:step2', args=[convention.uuid]) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm()

    programmes = services.conventions_step1(request)
    return render(request, "conventions/step1.html", {'form': form, 'programmes': programmes})


def convention_select_programme_update(request, convention_uuid):
    #TODO: gestion du 404
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == 'POST':
#        if request.POST['convention_uuid'] is None:
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            lot = Lot.objects.get(uuid=form.cleaned_data['lot_uuid'])
            convention.lot=lot
            convention.programme_id=lot.programme_id
            convention.bailleur_id=lot.bailleur_id
            convention.financement=lot.financement
            convention.save()
            # All is OK -> Next:
            return HttpResponseRedirect(reverse('conventions:step2', args=[convention.uuid]) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm(initial={'lot_uuid': str(convention.lot.uuid),})

    programmes = services.conventions_step1(request)
    return render(request, "conventions/step1.html", {'form': form, 'convention_uuid': convention_uuid, 'programmes': programmes})

def step3(request):
    return render(request, "conventions/step3.html")
def step4(request):
    return render(request, "conventions/step4.html")
def step5(request):
    return render(request, "conventions/step5.html")
def step6(request):
    return render(request, "conventions/step6.html")
def step7(request):
    return render(request, "conventions/step7.html")
def step8(request):
    return render(request, "conventions/step8.html")
def stepfin(request):
    return render(request, "conventions/stepfin.html")
