import re

from django.core.management.base import BaseCommand
from django.db.models import Count

from programmes.models import Programme


class Command(BaseCommand):

    def handle(self, *args, **options):
        duplicate_numero_operations = (
            # cas simple, on ne s'occupe que des programmes de conventions pas des programmes des avenants
            Programme.objects.filter(parent_id__isnull=True)
            # cas simple, on ne s'occupe que des programmes qui ont un numéro d'opération qui commence par 4 chiffres
            .filter(numero_operation__regex=r"^\d{4}")
            .values("numero_operation")
            .annotate(count=Count("id"))
            .filter(count=2)
        )
        count = 0
        for operation in duplicate_numero_operations:
            programmes = Programme.objects.filter(
                numero_operation=operation["numero_operation"]
            )
            # cas simple, on ne s'occupe que des programmes qui n'ont pas d'avenant
            if Programme.objects.filter(
                parent_id__in=[p.id for p in programmes]
            ).exists():
                continue
            # cas simple, on ne s'occupe que des programmes en double
            if programmes.count() != 2:
                continue
            financements = []
            to_continue = False
            for programme in programmes:
                # cas simple : on veut un seul lot par programme
                if programme.lots.count() != 1:
                    to_continue = True
                    break
                financements.append(programme.lots.first().financement)
            if to_continue:
                continue
            # cas simple, les lot sont tous de financement différent
            if len(set(financements)) != 2:
                continue

            programme_to_keep = programmes[0]
            programme_to_delete = programmes[1]

            to_continue = False
            for field in [
                "bailleur_id",
                "administration_id",
            ]:
                if getattr(programme_to_delete, field) != getattr(
                    programme_to_keep, field
                ):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Opération {operation['numero_operation']} ignorée car"
                            f" {field} : {getattr(programme_to_keep, field)} !="
                            f" {getattr(programme_to_delete, field)}"
                        )
                    )
                    to_continue = True
                    break
            if to_continue:
                continue
            for field in [
                "adresse",
                "code_postal",
                "ville",
                "code_insee_commune",
                "code_insee_departement",
                "code_insee_region",
                "annee_gestion_programmation",
                "zone_123",
                "zone_abc",
                "surface_corrigee_totale",
                "type_operation",
                "nature_logement",
                "anru",
                "nb_locaux_commerciaux",
                "nb_bureaux",
                "autres_locaux_hors_convention",
                "date_acte_notarie",
                "mention_publication_edd_volumetrique",
                "mention_publication_edd_classique",
                "permis_construire",
                "date_achevement_previsible",
                "date_achat",
                "date_achevement",
                "date_autorisation_hors_habitat_inclusif",
                "date_convention_location",
                "date_residence_argement_gestionnaire_intermediation",
                "departement_residence_argement_gestionnaire_intermediation",
                "ville_signature_residence_agrement_gestionnaire_intermediation",
                "date_achevement_compile",
                "cree_le",
                "mis_a_jour_le",
                "reassign_command_old_admin_backup",
            ]:
                to_delete_value = getattr(programme_to_delete, field)
                to_keep_value = getattr(programme_to_keep, field)
                if to_delete_value and not to_keep_value:
                    setattr(programme_to_keep, field, to_delete_value)

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
                "edd_stationnements",
            ]:
                to_delete_value = getattr(programme_to_delete, field)
                to_keep_value = getattr(programme_to_keep, field)
                if (
                    to_delete_value
                    and to_keep_value
                    and len(to_delete_value) > len(to_keep_value)
                ):
                    setattr(programme_to_keep, field, to_delete_value)
            # sommer les surface utiles
            programme_to_keep.surface_utile_totale = (
                (programme_to_keep.surface_utile_totale or 0)
                + (programme_to_delete.surface_utile_totale or 0)
            ) or None

            # gestion du nom
            matching = re.match(r"(.*)( - \d+ - \w{3,4})", programme_to_delete.nom)
            if matching:
                programme_to_keep.nom = f"{programme_to_keep.nom}{matching.group(2)}"

            programme_to_keep.save()
            for lot in programme_to_delete.lots.all():
                lot.programme = programme_to_keep
                lot.save()
                for convention in lot.conventions.all():
                    convention.programme = programme_to_keep
                    convention.save()
            self.stdout.write(
                self.style.SUCCESS(f"Programme {programme_to_delete.id} supprimé")
            )
            programme_to_delete.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Remplacé par  {programme_to_keep.id} - {programme_to_keep.numero_operation}"
                )
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Total : {count}"))
