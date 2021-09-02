import datetime

from io import BytesIO
from enum import Enum
from zipfile import BadZipFile
from openpyxl import load_workbook

from conventions.models import Convention, Preteur, Pret
from programmes.models import Lot
from programmes.forms import (
    ProgrammeSelectionForm,
    ProgrammeForm,
    ProgrammmeCadastralForm,
)
from programmes.forms import LogementFormSet
from bailleurs.forms import BailleurForm
from .forms import (
    ConventionCommentForm,
    ConventionFinancementForm,
    PretFormSet,
    UploadForm,
)

class ReturnStatus(Enum):
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    WARNING = 'WARNING'

def format_date_for_form(date):
    return date.strftime("%Y-%m-%d") if date is not None else ""


def conventions_index(request, infilter):
    infilter.update(request.user.convention_filter())
    conventions = Convention.objects.prefetch_related("programme").filter(**infilter)
    return conventions


def conventions_step1(request, infilter):
    infilter.update(request.user.programme_filter())
    return (
        Lot.objects.prefetch_related("programme")
        .prefetch_related("convention_set")
        .filter(**infilter)
        .order_by("programme__nom", "financement")
    )


def select_programme_create(request):
    if request.method == "POST":
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            lot = Lot.objects.get(uuid=form.cleaned_data["lot_uuid"])
            convention = Convention.objects.create(
                lot=lot,
                programme_id=lot.programme_id,
                bailleur_id=lot.bailleur_id,
                financement=lot.financement,
            )
            convention.save()
            # All is OK -> Next:
            return {
                "success": ReturnStatus.SUCCESS,
                "convention": convention,
                "form": form,
            }  # HttpResponseRedirect(reverse('conventions:step2', args=[convention.uuid]) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm()

    programmes = conventions_step1(request, {})
    return {
        "success": ReturnStatus.ERROR,
        "programmes": programmes,
        "form": form,
    }  # render(request, "conventions/step1.html", {'form': form, 'programmes': programmes})


def select_programme_update(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == "POST":
        #        if request.POST['convention_uuid'] is None:
        form = ProgrammeSelectionForm(request.POST)
        if form.is_valid():
            lot = Lot.objects.get(uuid=form.cleaned_data["lot_uuid"])
            convention.lot = lot
            convention.programme_id = lot.programme_id
            convention.bailleur_id = lot.bailleur_id
            convention.financement = lot.financement
            convention.save()
            # All is OK -> Next:
            return {"success": ReturnStatus.SUCCESS, "convention": convention, "form": form}

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeSelectionForm(
            initial={
                "lot_uuid": str(convention.lot.uuid),
            }
        )

    programmes = conventions_step1(request, {})
    return {
        "success": ReturnStatus.ERROR,
        "programmes": programmes,
        "convention_uuid": convention_uuid,
        "form": form,
    }


def bailleur_update(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    bailleur = convention.bailleur

    if request.method == "POST":
        #        if request.POST['convention_uuid'] is None:
        form = BailleurForm(request.POST)
        if form.is_valid():
            bailleur.nom = form.cleaned_data["nom"]
            bailleur.siret = form.cleaned_data["siret"]
            bailleur.capital_social = form.cleaned_data["capital_social"]
            bailleur.adresse = form.cleaned_data["adresse"]
            bailleur.code_postal = form.cleaned_data["code_postal"]
            bailleur.ville = form.cleaned_data["ville"]
            bailleur.dg_nom = form.cleaned_data["dg_nom"]
            bailleur.dg_fonction = form.cleaned_data["dg_fonction"]
            bailleur.dg_date_deliberation = form.cleaned_data["dg_date_deliberation"]
            bailleur.save()
            # All is OK -> Next:
            return {"success": ReturnStatus.SUCCESS, "convention": convention, "form": form}

    # If this is a GET (or any other method) create the default form.
    else:
        form = BailleurForm(
            initial={
                "nom": bailleur.nom,
                "siret": bailleur.siret,
                "capital_social": bailleur.capital_social,
                "adresse": bailleur.adresse,
                "code_postal": bailleur.code_postal,
                "ville": bailleur.ville,
                "dg_nom": bailleur.dg_nom,
                "dg_fonction": bailleur.dg_fonction,
                "dg_date_deliberation": format_date_for_form(
                    bailleur.dg_date_deliberation
                ),
            }
        )

    return {"success": ReturnStatus.ERROR, "convention": convention, "form": form}


def programme_update(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    programme = convention.programme

    if request.method == "POST":
        #        if request.POST['convention_uuid'] is None:
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme.adresse = form.cleaned_data["adresse"]
            programme.code_postal = form.cleaned_data["code_postal"]
            programme.ville = form.cleaned_data["ville"]
            programme.nb_logements = form.cleaned_data["nb_logements"]
            programme.type_habitat = form.cleaned_data["type_habitat"]
            programme.type_operation = form.cleaned_data["type_operation"]
            programme.anru = form.cleaned_data["anru"]
            programme.autre_locaux_hors_convention = form.cleaned_data[
                "autre_locaux_hors_convention"
            ]
            programme.nb_locaux_commerciaux = form.cleaned_data["nb_locaux_commerciaux"]
            programme.nb_bureaux = form.cleaned_data["nb_bureaux"]
            programme.save()
            # All is OK -> Next:
            return {"success": ReturnStatus.SUCCESS, "convention": convention, "form": form}

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProgrammeForm(
            initial={
                "adresse": programme.adresse,
                "code_postal": programme.code_postal,
                "ville": programme.ville,
                "nb_logements": programme.nb_logements,
                "type_habitat": programme.type_habitat,
                "type_operation": programme.type_operation,
                "anru": programme.anru,
                "autre_locaux_hors_convention": programme.autre_locaux_hors_convention,
                "nb_locaux_commerciaux": programme.nb_locaux_commerciaux,
                "nb_bureaux": programme.nb_bureaux,
            }
        )

    return {"success": ReturnStatus.ERROR, "convention": convention, "form": form}


def programme_cadastral_update(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    programme = convention.programme

    if request.method == "POST":
        form = ProgrammmeCadastralForm(request.POST)
        if form.is_valid():
            programme.permis_construire = form.cleaned_data["permis_construire"]
            programme.date_acte_notarie = form.cleaned_data["date_acte_notarie"]
            programme.date_achevement_previsible = form.cleaned_data[
                "date_achevement_previsible"
            ]
            programme.date_achat = form.cleaned_data["date_achat"]
            programme.date_achevement = form.cleaned_data["date_achevement"]
            programme.vendeur = form.cleaned_data["vendeur"]
            programme.acquereur = form.cleaned_data["acquereur"]
            programme.reference_notaire = form.cleaned_data["reference_notaire"]
            programme.reference_publication_acte = form.cleaned_data[
                "reference_publication_acte"
            ]
            programme.save()
            # All is OK -> Next:
            return {"success": ReturnStatus.SUCCESS, "convention": convention, "form": form}
    else:
        form = ProgrammmeCadastralForm(
            initial={
                "permis_construire": programme.permis_construire,
                "date_acte_notarie": format_date_for_form(programme.date_acte_notarie),
                "date_achevement_previsible": format_date_for_form(
                    programme.date_achevement_previsible
                ),
                "date_achat": format_date_for_form(programme.date_achat),
                "date_achevement": format_date_for_form(programme.date_achevement),
                "vendeur": programme.vendeur,
                "acquereur": programme.acquereur,
                "reference_notaire": programme.reference_notaire,
                "reference_publication_acte": programme.reference_publication_acte,
            }
        )

    return {"success": ReturnStatus.ERROR, "convention": convention, "form": form}


def convention_financement(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    import_errors = None
    import_warnings = None

    if request.method == "POST":
        # When the user cliked on "Téléverser" button
        if request.POST.get("Upload", False):
            form = ConventionFinancementForm(request.POST)
            formset = PretFormSet(request.POST)
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                result = handle_uploaded_file(request.FILES["file"], Pret)
                if result['success'] != ReturnStatus.ERROR:
                    formset = PretFormSet(initial=result['objects'])
                    import_warnings = result['import_warnings']
                else:
                    import_errors = result['errors']
        # When the user cliked on "Enregistrer et Suivant"
        else:
            form = ConventionFinancementForm(request.POST)
            formset = PretFormSet(request.POST)
            upform = UploadForm()
            form_is_valid = form.is_valid()
            formset_is_valid = formset.is_valid()
            if form_is_valid and formset_is_valid:
                convention.date_fin_conventionnement = form.cleaned_data[
                    "date_fin_conventionnement"
                ]
                convention.fond_propre = form.cleaned_data[
                    "fond_propre"
                ]
                convention.save()
                # MANAGE formset save in DB
                convention.pret_set.all().delete()
                for form_pret in formset:
                    pret = Pret.objects.create(
                        convention=convention,
                        bailleur=convention.bailleur,
                        numero=form_pret.cleaned_data["numero"],
                        date_octroi=form_pret.cleaned_data["date_octroi"],
                        duree=form_pret.cleaned_data["duree"],
                        montant=form_pret.cleaned_data["montant"],
                        preteur=form_pret.cleaned_data["preteur"],
                        #                        autre = form_pret.cleaned_data['autre'],
                    )
                    pret.save()

                # All is OK -> Next:
                return {
                    "success": ReturnStatus.SUCCESS,
                    "convention": convention,
                    "form": form,
                    "formset": formset,
                }
    # When display the file for the first time
    else:
        initial = []
        prets = convention.pret_set.all()
        for pret in prets:
            initial.append(
                {
                    "numero": pret.numero,
                    "date_octroi": format_date_for_form(pret.date_octroi),
                    "duree": pret.duree,
                    "montant": pret.montant,
                    "preteur": pret.preteur,
                }
            )
        upform = UploadForm()
        formset = PretFormSet(initial=initial)
        form = ConventionFinancementForm(
            initial={
                "date_fin_conventionnement": format_date_for_form(
                    convention.date_fin_conventionnement
                ),
                "fond_propre": convention.fond_propre,
            }
        )
    return {
        "success": ReturnStatus.ERROR,
        "convention": convention,
        "form": form,
        "formset": formset,
        "upform": upform,
        "import_errors": import_errors,
        "import_warnings": import_warnings,
    }


def logements_update(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == "POST":

        if request.POST.get("Upload", False):
            formset = PretFormSet(request.POST)
            upform = UploadForm(request.POST, request.FILES)
            if upform.is_valid():
                print("todo")
        # When the user cliked on "Enregistrer et Suivant"
        else:
            formset = LogementFormSet(request.POST)
            upform = UploadForm()
            print("todo")

            return {"success": ReturnStatus.SUCCESS, "convention": convention}

    else:
        initial = []
        logements = convention.lot.logement_set.all()
        for logement in logements:
            initial.append({"designation": logement.designation})
        if len(initial) == 0:
            initial.append(
                {
                    "designation": "123456789",
                    "typologie": "T2",
                    "surface_habitable": 60.56,
                    "surface_annexes": 12.4,
                    "surface_annexes_retenue": 6.2,
                    "surface_utile": 66.72,
                    "loyer_par_metre_carre": 5.2,
                    "coeficient": 1,
                    "loyer": 347,
                }
            )
            initial.append(
                {
                    "designation": "987654321",
                    "typologie": "",
                    "surface_habitable": "",
                    "surface_annexes": "",
                    "surface_annexes_retenue": "",
                    "surface_utile": "",
                    "loyer_par_metre_carre": "",
                    "coeficient": "",
                    "loyer": "",
                }
            )
        formset = LogementFormSet(initial=initial)
        upform = UploadForm()

    return {
        "success": ReturnStatus.ERROR,
        "convention": convention,
        "formset": formset,
        "upform": upform,
    }


def convention_comments(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)

    if request.method == "POST":
        form = ConventionCommentForm(request.POST)
        if form.is_valid():
            convention.comments = form.cleaned_data["comments"]
            convention.save()
            # All is OK -> Next:
            return {"success": ReturnStatus.SUCCESS, "convention": convention, "form": form}

    else:
        form = ConventionCommentForm(
            initial={
                "comments": convention.comments,
            }
        )

    return {"success": ReturnStatus.ERROR, "convention": convention, "form": form}


def handle_uploaded_file(my_file, myClass):
    import_mapping = myClass.import_mapping
    try:
        my_wb = load_workbook(filename=BytesIO(my_file.read()))
    except BadZipFile:
        return {
            "success": ReturnStatus.ERROR,
            'errors':[Exception(
                "Le fichier importé ne semble pas être du bon format, 'xlsx' est le format attendu"
            )]
        }

    try:
        my_ws = my_wb[myClass.sheet_name]
    except KeyError:
        return {
            "success": ReturnStatus.ERROR,
            'errors': [Exception(
                f"Le fichier importé doit avoir une feuille nommée '{myClass.sheet_name}'"
            )]
        }
    import_warnings = []
    column_from_index = {}
    for col in my_ws.iter_cols(min_col=1, max_col=my_ws.max_column, min_row=1, max_row=1):
        for cell in col:
            if cell.value is None:
                continue
            if cell.value not in import_mapping:
                import_warnings.append(Exception(
                    f"La colonne nommée '{cell.value}' est inconnue, elle sera ignorée. " +
                    f"Les colonnes attendues sont : {', '.join(import_mapping.keys())}"
                ))
                continue
            column_from_index[cell.column] = str(cell.value).strip()

    # transform each line into object
    my_objects = []
    for row in my_ws.iter_rows(
        min_row=2, max_row=my_ws.max_row, min_col=1, max_col=my_ws.max_column
    ):
        my_row, empty_line, new_warnings = extract_row(row, column_from_index, import_mapping)
        import_warnings = [*import_warnings, *new_warnings]

        # Ignore if the line is empty
        if not empty_line:
            my_objects.append(my_row)

    return {
        "success": ReturnStatus.SUCCESS if len(import_warnings) == 0 else ReturnStatus.WARNING,
        'objects': my_objects,
        "import_warnings": import_warnings,
    }


def extract_row(row, column_from_index, import_mapping):
    # pylint: disable=R0912
    new_warnings = []
    my_row = {}
    empty_line = True
    for cell in row:
        # Ignore unknown column
        if cell.column not in column_from_index:
            continue

        # Check the empty lines to don't fill it
        if cell.value:
            empty_line = False
        else:
            continue


        value = None
        model_field = import_mapping[column_from_index[cell.column]]

        # Date case
        if model_field.get_internal_type() == 'DateField':
            if isinstance(cell.value, datetime.datetime):
                value = format_date_for_form(cell.value)
            else:
                new_warnings.append(Exception(
                    f"{cell.column_letter}{cell.row} : La valeur '{cell.value}' " +
                    f"de la colonne {column_from_index[cell.column]} " +
                    "doit être une date"
                ))

        # TextChoices case
        elif (model_field.get_internal_type() == 'CharField' and
                model_field.choices is not None):
            if cell.value is not None:
                value = next((x[0] for x in model_field.choices if x[1] == cell.value), None)
                if value is None: # value is not Null but not in the choices neither
                    new_warnings.append(Exception(
                        f"{cell.column_letter}{cell.row} : La valeur '{cell.value}' " +
                        f"de la colonne {column_from_index[cell.column]} " +
                        f"doit faire partie des valeurs : {', '.join(Preteur.labels)}"
                    ))

        # Float case
        elif model_field.get_internal_type() == 'FloatField':
            if cell.value is not None:
                if isinstance(cell.value, (float, int)):
                    value = float(cell.value)
                else:
                    new_warnings.append(Exception(
                        f"{cell.column_letter}{cell.row} : La valeur '{cell.value}' " +
                        f"de la colonne {column_from_index[cell.column]} " +
                        "doit être une valeur numérique"
                    ))

        # Integer case
        elif model_field.get_internal_type() == 'IntegerField':
            if cell.value is not None:
                if isinstance(cell.value, (float, int)):
                    value = int(cell.value)
                else:
                    new_warnings.append(Exception(
                        f"{cell.column_letter}{cell.row} : La valeur '{cell.value}' " +
                        f"de la colonne {column_from_index[cell.column]} " +
                        "doit être une valeur numérique"
                    ))

        # String case
        elif model_field.get_internal_type() == 'CharField':
            if cell.value is not None:
                if isinstance(cell.value, (float, int, str)):
                    value = cell.value
                else:
                    new_warnings.append(Exception(
                        f"{cell.column_letter}{cell.row} : La valeur '{cell.value}' " +
                        f"de la colonne {column_from_index[cell.column]} " +
                        "doit être une valeur alphanumeric"
                    ))
        my_row[model_field.name] = value

    return my_row, empty_line, new_warnings
