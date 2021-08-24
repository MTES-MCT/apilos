from conventions.models import Convention
from programmes.models import Lot
from programmes.forms import ProgrammeSelectionForm, ProgrammeForm, ProgrammmeCadastralForm
from .forms import ConventionCommentForm, ConventionFinancementForm
from bailleurs.forms import BailleurForm

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

def format_date_for_form(date):
    return date.strftime("%Y-%m-%d") if date is not None else ''

def conventions_index(request, infilter):
    infilter.update(request.user.convention_filter())
    conventions = Convention.objects.prefetch_related('programme').filter(**infilter)
    return conventions

def conventions_step1(request, infilter):
    infilter.update(request.user.programme_filter())
    return Lot.objects.prefetch_related('programme').prefetch_related('convention_set').filter(**infilter).order_by('programme__nom', 'financement')

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

    programmes = conventions_step1(request, {})
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
            return {'success':True, 'convention':convention, 'form':form}

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm(initial={'lot_uuid': str(convention.lot.uuid),})

    programmes = conventions_step1(request, {})
    return {'success':False, 'programmes':programmes, 'convention_uuid': convention_uuid, 'form':form}


def bailleur_update(request, convention_uuid):
    #TODO: gestion du 404
    convention = Convention.objects.get(uuid=convention_uuid)
    bailleur = convention.bailleur

    if request.method == 'POST':
#        if request.POST['convention_uuid'] is None:
        form = BailleurForm(request.POST)
        if form.is_valid():
            bailleur.nom = form.cleaned_data['nom']
            bailleur.siret = form.cleaned_data['siret']
            bailleur.capital_social = form.cleaned_data['capital_social']
            bailleur.adresse = form.cleaned_data['adresse']
            bailleur.code_postal = form.cleaned_data['code_postal']
            bailleur.ville = form.cleaned_data['ville']
            bailleur.dg_nom = form.cleaned_data['dg_nom']
            bailleur.dg_fonction = form.cleaned_data['dg_fonction']
            bailleur.dg_date_deliberation = form.cleaned_data['dg_date_deliberation']
            bailleur.save()
            # All is OK -> Next:
            return {'success':True, 'convention':convention, 'form':form}

    # If this is a GET (or any other method) create the default form.
    else:
        form = BailleurForm(initial={
            'nom': bailleur.nom,
            'siret': bailleur.siret,
            'capital_social': bailleur.capital_social,
            'adresse': bailleur.adresse,
            'code_postal': bailleur.code_postal,
            'ville': bailleur.ville,
            'dg_nom': bailleur.dg_nom,
            'dg_fonction': bailleur.dg_fonction,
            'dg_date_deliberation': format_date_for_form(bailleur.dg_date_deliberation),
        })

    return {'success':False, 'convention': convention, 'form':form}

def programme_update(request, convention_uuid):
    #TODO: gestion du 404
    convention = Convention.objects.get(uuid=convention_uuid)
    programme = convention.programme

    if request.method == 'POST':
#        if request.POST['convention_uuid'] is None:
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme.adresse = form.cleaned_data['adresse']
            programme.code_postal = form.cleaned_data['code_postal']
            programme.ville = form.cleaned_data['ville']
            programme.nb_logements = form.cleaned_data['nb_logements']
            programme.type_habitat = form.cleaned_data['type_habitat']
            programme.type_operation = form.cleaned_data['type_operation']
            programme.anru = form.cleaned_data['anru']
            programme.nb_logement_non_conventionne = form.cleaned_data['nb_logement_non_conventionne']
            programme.nb_locaux_commerciaux = form.cleaned_data['nb_locaux_commerciaux']
            programme.nb_bureaux = form.cleaned_data['nb_bureaux']
            programme.save()
            # All is OK -> Next:
            return {'success':True, 'convention':convention, 'form':form}

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeForm(initial={
            'adresse': programme.adresse,
            'code_postal': programme.code_postal,
            'ville': programme.ville,
            'nb_logements': programme.nb_logements,
            'type_habitat': programme.type_habitat,
            'type_operation': programme.type_operation,
            'anru': programme.anru,
            'nb_logement_non_conventionne': programme.nb_logement_non_conventionne,
            'nb_locaux_commerciaux': programme.nb_locaux_commerciaux,
            'nb_bureaux': programme.nb_bureaux,
        })

    return {'success':False, 'convention': convention, 'form':form}


def programme_cadastral_update(request, convention_uuid):
    #TODO: gestion du 404
    convention = Convention.objects.get(uuid=convention_uuid)
    programme = convention.programme

    if request.method == 'POST':
        form = ProgrammmeCadastralForm(request.POST)
        if form.is_valid():
            programme.permis_construire = form.cleaned_data['permis_construire']
            programme.date_acte_notarie = form.cleaned_data['date_acte_notarie']
            programme.date_achevement_previsible = form.cleaned_data['date_achevement_previsible']
            programme.date_achat = form.cleaned_data['date_achat']
            programme.date_achevement = form.cleaned_data['date_achevement']
            programme.vendeur = form.cleaned_data['vendeur']
            programme.acquereur = form.cleaned_data['acquereur']
            programme.reference_notaire = form.cleaned_data['reference_notaire']
            programme.reference_publication_acte = form.cleaned_data['reference_publication_acte']
            programme.save()
            # All is OK -> Next:
            return {'success':True, 'convention':convention, 'form':form}
    else:
        form = ProgrammmeCadastralForm(initial={
            'permis_construire': programme.permis_construire,
            'date_acte_notarie': format_date_for_form(programme.date_acte_notarie),
            'date_achevement_previsible': format_date_for_form(programme.date_achevement_previsible),
            'date_achat': format_date_for_form(programme.date_achat),
            'date_achevement': format_date_for_form(programme.date_achevement),
            'vendeur': programme.vendeur,
            'acquereur': programme.acquereur,
            'reference_notaire': programme.reference_notaire,
            'reference_publication_acte': programme.reference_publication_acte,
        })

    return {'success':False, 'convention': convention, 'form':form}


def convention_financement(request, convention_uuid):
    #TODO: gestion du 404
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == 'POST':
        form = ConventionFinancementForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['date_fin_conventionnement'])
            convention.date_fin_conventionnement = form.cleaned_data['date_fin_conventionnement']
            convention.save()
            # All is OK -> Next:
            return {'success':True, 'convention':convention, 'form':form}

    else:
        form = ConventionFinancementForm(initial={
            'date_fin_conventionnement': format_date_for_form(convention.date_fin_conventionnement),
        })

    return {'success':False, 'convention': convention, 'form':form}


def convention_comments(request, convention_uuid):
    #TODO: gestion du 404
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == 'POST':
        form = ConventionCommentForm(request.POST)
        if form.is_valid():
            convention.comments = form.cleaned_data['comments']
            convention.save()
            # All is OK -> Next:
            return {'success':True, 'convention':convention, 'form':form}

    else:
        form = ConventionCommentForm(initial={
            'comments': convention.comments,
        })

    return {'success':False, 'convention': convention, 'form':form}
