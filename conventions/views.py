from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from programmes.models import TypeHabitat, TypeOperation
from .models import Preteur
from . import services


NB_STEPS = 9

@permission_required('convention.view_convention')
def index(request):
    conventions = services.conventions_index(request, {})
    return render(request, "conventions/index.html", {'conventions': conventions, 'filter': request.user.convention_filter()})

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
        return render(request, "conventions/step1.html", {
            'form': result['form'],
            'convention_uuid': result['convention_uuid'],
            'programmes': result['programmes'],
            'nb_steps': NB_STEPS,
        })

@permission_required('convention.change_convention')
def step2(request, convention_uuid):
    result = services.bailleur_update(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step3', args=[result['convention'].uuid]) )
    else:
        return render(request, "conventions/step2.html", {
            'form': result['form'],
            'convention': result['convention'],
            'nb_steps': NB_STEPS,
        })

@permission_required('convention.change_convention')
def step3(request, convention_uuid):
    result = services.programme_update(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step4', args=[result['convention'].uuid]) )
    else:
        return render(request, "conventions/step3.html", {
            'form': result['form'],
            'convention': result['convention'],
            'nb_steps': NB_STEPS,
            'types_habitat': TypeHabitat,
            'types_operation': TypeOperation,
        })

@permission_required('convention.change_convention')
def step4(request, convention_uuid):
    result = services.programme_cadastral_update(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step5', args=[result['convention'].uuid]) )
    else:
        return render(request, "conventions/step4.html", {
            'form': result['form'],
            'convention': result['convention'],
            'nb_steps': NB_STEPS,
        })


from .forms import UploadForm

@permission_required('convention.change_convention')
def step5(request, convention_uuid):
    result = services.convention_financement(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step6', args=[result['convention'].uuid]) )
    else:
        return render(request, "conventions/step5.html", {
            'upform' : result['upform'],
            'form': result['form'],
            'formset': result['formset'],
            'convention': result['convention'],
            'nb_steps': NB_STEPS,
            'preteurs': Preteur,
        })


@permission_required('convention.change_convention')
def step6(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:step7', args=[result['convention'].uuid]) )
    else:
        print(result['formset'])
        return render(request, "conventions/step6.html", {
            'formset': result['formset'],
            'convention': result['convention'],
            'nb_steps': NB_STEPS,
        })

@permission_required('convention.change_convention')
def step7(request, convention_uuid):
    return render(request, "conventions/step7.html", {
        'convention_uuid': convention_uuid,
        'nb_steps': NB_STEPS,
    })

@permission_required('convention.change_convention')
def step8(request, convention_uuid):
    return render(request, "conventions/step8.html", {
        'convention_uuid': convention_uuid,
        'nb_steps': NB_STEPS,
    })

@permission_required('convention.change_convention')
def step9(request, convention_uuid):
    result = services.convention_comments(request, convention_uuid)
    if result['success']:
        return HttpResponseRedirect(reverse('conventions:stepfin', args=[result['convention'].uuid]) )
    else:
        return render(request, "conventions/step9.html", {
            'form': result['form'],
            'convention': result['convention'],
            'nb_steps': NB_STEPS,
        })

@permission_required('convention.change_convention')
def stepfin(request, convention_uuid):
    return render(request, "conventions/stepfin.html", {
        'convention_uuid': convention_uuid,
        'nb_steps': NB_STEPS,
    })




# Import mimetypes module
import mimetypes
# import os module
import os
# Import HttpResponse module
from django.http.response import HttpResponse


def download_convention_prets(request, convention_uuid):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = 'prets.xlsx'
    # Define the full file path
    filepath = BASE_DIR + '/static/files/' + filename

    if os.path.exists(filepath):
        with open(filepath, "rb") as excel:
            data = excel.read()

        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=prets.xlsx'
        return response




