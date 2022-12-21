from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import permission_required

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "selection",
        permission_required("convention.add_convention")(
            views.ConventionSelectionFromDBView.as_view()
        ),
        name="selection",
    ),
    path(
        "selection_from_zero",
        permission_required("convention.add_convention")(
            views.ConventionSelectionFromZeroView.as_view()
        ),
        name="selection_from_zero",
    ),
    path(
        "bailleur/<convention_uuid>",
        views.ConventionBailleurView.as_view(),
        name="bailleur",
    ),
    path(
        "avenant_bailleur/<convention_uuid>",
        views.AvenantBailleurView.as_view(),
        name="avenant_bailleur",
    ),
    path(
        "programme/<convention_uuid>",
        views.ConventionProgrammeView.as_view(),
        name="programme",
    ),
    path(
        "cadastre/<convention_uuid>",
        views.ConventionCadastreView.as_view(),
        name="cadastre",
    ),
    path("edd/<convention_uuid>", views.ConventionEDDView.as_view(), name="edd"),
    path(
        "financement/<convention_uuid>",
        views.ConventionFinancementView.as_view(),
        name="financement",
    ),
    path(
        "avenant_financement/<convention_uuid>",
        views.AvenantFinancementView.as_view(),
        name="avenant_financement",
    ),
    path(
        "logements/<convention_uuid>",
        views.ConventionLogementsView.as_view(),
        name="logements",
    ),
    path(
        "avenant_logements/<convention_uuid>",
        views.AvenantLogementsView.as_view(),
        name="avenant_logements",
    ),
    path(
        "foyer_residence_logements/<convention_uuid>",
        views.ConventionFoyerResidenceLogementsView.as_view(),
        name="foyer_residence_logements",
    ),
    path(
        "avenant_foyer_residence_logements/<convention_uuid>",
        views.AvenantFoyerResidenceLogementsView.as_view(),
        name="avenant_foyer_residence_logements",
    ),
    path(
        "annexes/<convention_uuid>",
        views.ConventionAnnexesView.as_view(),
        name="annexes",
    ),
    path(
        "avenant_annexes/<convention_uuid>",
        views.AvenantAnnexesView.as_view(),
        name="avenant_annexes",
    ),
    path(
        "collectif/<convention_uuid>",
        views.ConventionCollectifView.as_view(),
        name="collectif",
    ),
    path(
        "avenant_collectif/<convention_uuid>",
        views.AvenantCollectifView.as_view(),
        name="avenant_collectif",
    ),
    path(
        "stationnements/<convention_uuid>",
        views.ConventionTypeStationnementView.as_view(),
        name="stationnements",
    ),
    path(
        "attribution/<convention_uuid>",
        views.ConventionFoyerAttributionView.as_view(),
        name="attribution",
    ),
    path(
        "variantes/<convention_uuid>",
        views.ConventionFoyerVariantesView.as_view(),
        name="variantes",
    ),
    path(
        "comments/<convention_uuid>",
        views.ConventionCommentsView.as_view(),
        name="comments",
    ),
    path(
        "avenant_comments/<convention_uuid>",
        views.AvenantCommentsView.as_view(),
        name="avenant_comments",
    ),
    path("recapitulatif/<convention_uuid>", views.recapitulatif, name="recapitulatif"),
    path(
        "save/<convention_uuid>",
        views.save_convention,
        name="save",
    ),
    path(
        "delete/<convention_uuid>",
        views.delete_convention,
        name="delete",
    ),
    path(
        "feedback/<convention_uuid>",
        views.feedback_convention,
        name="feedback",
    ),
    path(
        "validate/<convention_uuid>",
        views.validate_convention,
        name="validate",
    ),
    path(
        "generate/<convention_uuid>",
        views.generate_convention,
        name="generate",
    ),
    path(
        "load_xlsx_model/<file_type>",
        views.load_xlsx_model,
        name="load_xlsx_model",
    ),
    path(
        "preview/<convention_uuid>",
        views.preview,
        name="preview",
    ),
    path(
        "sent/<convention_uuid>",
        views.sent,
        name="sent",
    ),
    path(
        "post_action/<convention_uuid>",
        views.post_action,
        name="post_action",
    ),
    path(
        "display_pdf/<convention_uuid>",
        views.display_pdf,
        name="display_pdf",
    ),
    path(
        "fiche_caf/<convention_uuid>",
        views.fiche_caf,
        name="fiche_caf",
    ),
    path("new_avenant/<convention_uuid>", views.new_avenant, name="new_avenant"),
    path("piece_jointe/<piece_jointe_uuid>", views.piece_jointe_access, name="piece_jointe"),
    path(
        "piece_jointe/<piece_jointe_uuid>/promote",
        views.piece_jointe_promote,
        name="piece_jointe_promote",
    ),
    path(
        "new_avenant_start",
        TemplateView.as_view(
            template_name="conventions/avenant/new_avenant_start.html"
        ),
        name="new_avenant_start",
    ),
    path(
        "search_for_avenant",
        TemplateView.as_view(
            template_name="conventions/avenant/search_for_avenant.html"
        ),
        name="search_for_avenant",
    ),
    path(
        "search_for_avenant_result",
        permission_required("convention.add_convention")(
            views.SearchForAvenantResultView.as_view()
        ),
        name="search_for_avenant_result",
    ),
    path(
        "new_avenants_for_avenant/<convention_uuid>",
        views.new_avenants_for_avenant,
        name="new_avenants_for_avenant",
    ),
    path(
        "form_avenants_for_avenant/<convention_uuid>",
        views.form_avenants_for_avenant,
        name="form_avenants_for_avenant",
    ),
]
