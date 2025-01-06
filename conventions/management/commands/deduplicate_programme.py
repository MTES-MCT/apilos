import json

from django.core.management.base import BaseCommand
from django.db.models import Count

from programmes.models import Programme


class Command(BaseCommand):
    def handle(self, *args, **options):
        num_galion = {
            v["numero_operation"]
            for v in Programme.objects.filter(parent_id=None)
            .exclude(numero_operation=None)
            .exclude(numero_operation="")
            .values("numero_operation")
            .annotate(Count("id"))
            .order_by()
            .filter(id__count__gt=1)
        }

        count = 0
        failed = []
        for num in num_galion:
            programmes = (
                Programme.objects.select_related("bailleur")
                .select_related("administration")
                .filter(numero_operation=num)
            )
            conventions = [p.conventions for p in programmes]
            if (
                len({p.bailleur for p in programmes}) == 1
                and len({p.administration for p in programmes}) == 1
                and len({p.code_postal for p in programmes}) == 1
                and len(conventions) == programmes.count()
            ):
                # join if not unique
                count += 1
                for field in [
                    "nom",
                    "adresse",
                    "autres_locaux_hors_convention",
                    "permis_construire",
                    "departement_residence_argement_gestionnaire_intermediation",
                    "ville_signature_residence_agrement_gestionnaire_intermediation",
                    "mention_publication_edd_volumetrique",
                    "mention_publication_edd_classique",
                ]:
                    if len(values := {getattr(p, field) or "" for p in programmes}) > 1:
                        setattr(programmes[0], field, " / ".join(values)[:255])

                # get first not none
                for field in [
                    "ville",
                    "code_insee_commune",
                    "code_insee_departement",
                    "code_insee_region",
                    "annee_gestion_programmation",
                    "zone_123",
                    "zone_abc",
                    "type_operation",
                    "nature_logement",
                    "anru",
                    "date_acte_notarie",
                    "date_achevement_previsible",
                    "date_achat",
                    "date_achevement",
                    "date_autorisation_hors_habitat_inclusif",
                    "date_convention_location",
                    "date_residence_argement_gestionnaire_intermediation",
                    "date_achevement_compile",
                    "cree_le",
                    "mis_a_jour_le",
                ]:
                    setattr(
                        programmes[0],
                        field,
                        next(
                            (
                                getattr(p, field)
                                for p in programmes
                                if getattr(p, field)
                            ),
                            None,
                        ),
                    )
                # sum values
                for field in [
                    "surface_utile_totale",
                    "surface_corrigee_totale",
                    "nb_locaux_commerciaux",
                    "nb_bureaux",
                ]:
                    setattr(
                        programmes[0],
                        field,
                        sum(
                            (
                                getattr(p, field)
                                for p in programmes
                                if getattr(p, field)
                            ),
                            0,
                        ),
                    )
                # join json
                for field in [
                    "vendeur",
                    "acquereur",
                    "reference_notaire",
                    "reference_publication_acte",
                    "acte_de_propriete",
                    "effet_relatif",
                    "certificat_adressage",
                    "reference_cadastrale",
                    "edd_volumetrique",
                    "edd_classique",
                ]:
                    try:
                        field_values = [
                            json.loads(getattr(p, field))
                            for p in programmes
                            if getattr(p, field)
                        ]
                    except json.JSONDecodeError:
                        field_values = []
                        failed.append(num)
                    if len(field_values) > 1:
                        files = {}
                        texts = []
                        for d in field_values:
                            files.update(d.get("files", {}))
                            texts.append(d.get("text", ""))

                        setattr(
                            programmes[0],
                            field,
                            json.dumps({"files": files, "text": " / ".join(texts)}),
                        )
                programmes[0].anru = bool(programmes[0].anru)
                programmes[0].save()
                for p in programmes[1:]:
                    # FIXME : A supprimer quand lots n'a plus programme_id
                    for lot in p.lots.all():
                        lot.programme = programmes[0]
                        lot.save()
                    for convention in p.conventions.all():
                        convention.programme = programmes[0]
                        convention.save()
                    Programme.objects.filter(parent_id=p.id).update(
                        parent_id=programmes[0].id
                    )
                    p.delete()

        self.stdout.write(f"Total programmes to merge {count}")
        self.stdout.write(f"Failed {failed}")
