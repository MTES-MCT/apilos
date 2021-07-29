from conventions.models import Convention
from programmes.models import Lot
from .forms import ProgrammeSelectionForm


from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy


def conventions_index(request, infilter={}):
    infilter.update(request.user.convention_filter())
    conventions = Convention.objects.prefetch_related('programme').filter(**infilter)
    return conventions


def conventions_step1(request, infilter={}):
    infilter.update(request.user.programme_filter())
    return Lot.objects.prefetch_related('programme').filter(**infilter).order_by('programme__nom', 'financement')

def select_programme_create(request):
    if request.method == 'POST':
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            lot = Lot.objects.get(uuid=form.cleaned_data['lot_uuid'])
            convention = Convention.objects.create(lot=lot, programme_id=lot.programme_id, bailleur_id=lot.bailleur_id, financement=lot.financement)
            convention.save()
            # All is OK -> Next:
            return {'success':True, 'convention':convention, 'form':form} #HttpResponseRedirect(reverse('conventions:step2', args=[convention.uuid]) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm()

    programmes = conventions_step1(request)
    return {'success':False, 'programmes':programmes, 'form':form} # render(request, "conventions/step1.html", {'form': form, 'programmes': programmes})

def select_programme_update(request, convention_uuid):
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
            return {'success':True, 'convention':convention, 'form':form} #HttpResponseRedirect(reverse('conventions:step2', args=[convention.uuid]) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm(initial={'lot_uuid': str(convention.lot.uuid),})

    programmes = conventions_step1(request)
    return {'success':False, 'programmes':programmes, 'convention_uuid': convention_uuid, 'form':form}#render(request, "conventions/step1.html", {'form': form, 'convention_uuid': convention_uuid, 'programmes': programmes})
