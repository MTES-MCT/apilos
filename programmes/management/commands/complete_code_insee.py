import json
import os
import re
from collections import defaultdict

import requests
from django.core.management.base import BaseCommand

from core.utils import strip_accents
from programmes.models import Programme


class Command(BaseCommand):
    help = "Complete the empty code_insee field of the Programme model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            help="Output directory for the generated files",
            default=None,
        )

    def _print_status(self):
        total_count = Programme.objects.count()
        to_handle_count = Programme.objects.filter(code_insee_commune="").count()
        self.stdout.write(
            f"{to_handle_count}/{total_count} programmes sans code insee commune."
        )

    def _normalize(self, s: str) -> str:
        n_str = strip_accents(s)
        for c in ["(", ")", "-", "'"]:
            n_str = n_str.replace(c, " ")
        n_str = re.sub(" +", " ", n_str)
        n_str = n_str.upper().strip()
        n_str = n_str.replace("ST ", "SAINT ").replace("STE ", "SAINTE ")
        return n_str

    def _load_code_insee_ref(self) -> dict[list[dict[str, str]]]:
        """
        Chargement d'un tableau de correspondance code postal / (code INSEE, nom commune)
        """

        insee_table = defaultdict(list)

        response = requests.get(
            "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/correspondance-code-insee-code-postal/exports/json?lang=fr&timezone=Europe%2FBerlin"
        )
        response.raise_for_status()

        for entry in response.json():
            for postal_code in entry["postal_code"].split("/"):
                insee_table[postal_code].append(
                    {
                        "insee_com": entry["insee_com"],
                        "postal_code": postal_code,
                        "nom_comm": self._normalize(entry["nom_comm"]),
                    }
                )

        for entry in extra_code_insee_entries:
            insee_table[entry["postal_code"]].append(entry)

        return insee_table

    def handle(self, *args, **options):  # noqa: C901
        self._print_status()

        self.stdout.write("Chargement du référentiel des codes INSEE...")
        insee_table = self._load_code_insee_ref()

        errors_unknown_code_postal = []
        errors_unknown_commune = []
        errors_multiple_choices = []

        self.stdout.write("Processing...")
        for programme in Programme.objects.filter(code_insee_commune="").exclude(
            code_postal="", ville=""
        ):
            entries = insee_table.get(programme.code_postal, [])

            if not len(entries):
                errors_unknown_code_postal.append(programme.code_postal)
                continue

            if len(entries) == 1:
                programme.code_insee_commune = entries[0]["insee_com"]
                programme.save()
                continue

            if len(entries) > 1:
                commune = self._normalize(programme.ville)
                if not len(commune):
                    errors_unknown_commune.append(
                        f"Programme {programme.id} ({programme.code_postal})"
                    )
                    continue

                for entry in entries:
                    if entry["nom_comm"] == commune:
                        programme.code_insee_commune = entry["insee_com"]
                        programme.save()
                        break
                else:
                    errors_multiple_choices.append(
                        f"Programme {programme.id} ({programme.code_postal}, {commune})"
                    )

        errors_unknown_code_postal = sorted(list(set(errors_unknown_code_postal)))
        errors_multiple_choices = sorted(list(set(errors_multiple_choices)))
        errors_unknown_commune = sorted(list(set(errors_unknown_commune)))

        self.stdout.write("Traitement terminé.")
        self.stdout.write("Résultats:")
        self._print_status()

        if len(errors_unknown_code_postal):
            self.stdout.write(
                self.style.ERROR(
                    f"{len(errors_unknown_code_postal)} programmes au code postal inconnu."
                )
            )

        if len(errors_unknown_commune):
            self.stdout.write(
                self.style.ERROR(
                    f"{len(errors_unknown_commune)} programmes sans nom de commune."
                )
            )

        if len(errors_multiple_choices):
            self.stdout.write(
                self.style.ERROR(
                    f"{len(errors_multiple_choices)} programmes avec plusieurs choix possibles."
                )
            )

        if output_dir := options["output_dir"]:
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/insee_table.json", "w") as f:
                f.write(json.dumps(insee_table, indent=2))
            with open(f"{output_dir}/errors_unknown_code_postal.json", "w") as f:
                f.write(json.dumps(errors_unknown_code_postal, indent=2))
            with open(f"{output_dir}/errors_multiple_choices.json", "w") as f:
                f.write(json.dumps(errors_multiple_choices, indent=2))
            with open(f"{output_dir}/errors_unknown_commune.json", "w") as f:
                f.write(json.dumps(errors_unknown_commune, indent=2))
            self.stdout.write(f"Données enregistrées dans {output_dir}.")


extra_code_insee_entries = [
    {"insee_com": "49018", "postal_code": "49150", "nom_comm": "BAUGE EN ANJOU"},
    {"insee_com": "33067", "postal_code": "33710", "nom_comm": "BOURG SUR GIRONDE"},
    {"insee_com": "49092", "postal_code": "49120", "nom_comm": "CHEMILLE EN ANJOU"},
    {"insee_com": "24053", "postal_code": "24750", "nom_comm": "BOULAZAC ISLE MANOIRE"},
    {"insee_com": "14762", "postal_code": "14500", "nom_comm": "VIRE NORMANDIE"},
    {"insee_com": "22093", "postal_code": "22400", "nom_comm": "LAMBALLE ARMOR"},
    {"insee_com": "80598", "postal_code": "80860", "nom_comm": "NOUVION EN PONTHIEU"},
    {"insee_com": "60104", "postal_code": "60120", "nom_comm": "BRETEUIL SUR NOYE"},
    {"insee_com": "73010", "postal_code": "73410", "nom_comm": "ENTRELACS"},
    {
        "insee_com": "49377",
        "postal_code": "49140",
        "nom_comm": "RIVES DU LOIR EN ANJOU",
    },
    {
        "insee_com": "24026",
        "postal_code": "24330",
        "nom_comm": "BASSILLAC ET AUBEROCHE",
    },
    {"insee_com": "74010", "postal_code": "74370", "nom_comm": "ANNECY"},
    {"insee_com": "19123", "postal_code": "19360", "nom_comm": "MALEMORT"},
    {"insee_com": "59004", "postal_code": "59310", "nom_comm": "AIX EN PEVELE"},
    {"insee_com": "59526", "postal_code": "59230", "nom_comm": "SAINT AMAND"},
    {"insee_com": "59586", "postal_code": "59242", "nom_comm": "TEMPLEUVE EN PEVELE"},
    {"insee_com": "68070", "postal_code": "68350", "nom_comm": "BRUNSTATT DIDENHEIM"},
    {"insee_com": "76108", "postal_code": "76230", "nom_comm": "BOIS GUILLAUME"},
    {
        "insee_com": "78158",
        "postal_code": "78150",
        "nom_comm": "LE CHESNAY ROCQUENCOURT",
    },
    {"insee_com": "85008", "postal_code": "85430", "nom_comm": "AUBIGNY LES CLOUZEAUX"},
    {
        "insee_com": "25368",
        "postal_code": "25640",
        "nom_comm": "MARCHAUX CHAUDEFONTAINE",
    },
    {
        "insee_com": "62764",
        "postal_code": "62223",
        "nom_comm": "SAINT NICOLAS LEZ ARRAS",
    },
    {"insee_com": "31232", "postal_code": "31330", "nom_comm": "GRENADE SUR GARONNE"},
    {
        "insee_com": "59588",
        "postal_code": "59229",
        "nom_comm": "TETEGHEM COUDEKERQUE VILLAGE",
    },
    {"insee_com": "33344", "postal_code": "33350", "nom_comm": "PUJOLS SUR DORDOGNE"},
    {"insee_com": "59405", "postal_code": "59400", "nom_comm": "MOEUVRES"},
    {"insee_com": "67372", "postal_code": "67350", "nom_comm": "VAL DE MODER"},
    {"insee_com": "49200", "postal_code": "49770", "nom_comm": "LONGUENEE EN ANJOU"},
    {"insee_com": "49200", "postal_code": "49220", "nom_comm": "LONGUENEE EN ANJOU"},
    {"insee_com": "31277", "postal_code": "31530", "nom_comm": "LASSERRE PRADERE"},
    {"insee_com": "49301", "postal_code": "49230", "nom_comm": "SEVREMOINE"},
    {"insee_com": "50292", "postal_code": "50570", "nom_comm": "MARIGNY LE LOZON"},
    {"insee_com": "01130", "postal_code": "01340", "nom_comm": "BRESSE VALLONS"},
    {"insee_com": "49023", "postal_code": "49600", "nom_comm": "BEAUPREAU EN MAUGES"},
    {"insee_com": "39491", "postal_code": "39170", "nom_comm": "COTEAUX DU LIZON"},
    {"insee_com": "54079", "postal_code": "54700", "nom_comm": "BLENOD LES PAM"},
    {"insee_com": "28422", "postal_code": "28150", "nom_comm": "LES VILLAGES VOVEENS"},
    {"insee_com": "30112", "postal_code": "30730", "nom_comm": "FONS OUTRE GARDON"},
    {"insee_com": "25035", "postal_code": "25870", "nom_comm": "LES AUXONS"},
    {"insee_com": "24312", "postal_code": "24660", "nom_comm": "SANILHAC"},
    {"insee_com": "79179", "postal_code": "79320", "nom_comm": "MONCOUTANT SUR SEVRE"},
    {
        "insee_com": "41059",
        "postal_code": "41700",
        "nom_comm": "LE CONTROIS EN SOLOGNE",
    },
    {"insee_com": "76618", "postal_code": "76370", "nom_comm": "PETIT CAUX"},
    {"insee_com": "53136", "postal_code": "53200", "nom_comm": "LA ROCHE NEUVILLE"},
    {"insee_com": "86281", "postal_code": "86380", "nom_comm": "SAINT MARTIN LA PALLU"},
    {
        "insee_com": "48094",
        "postal_code": "48500",
        "nom_comm": "MASSEGROS CAUSSES GORGES",
    },
    {"insee_com": "85084", "postal_code": "85140", "nom_comm": "ESSARTS EN BOCAGE"},
    {"insee_com": "80621", "postal_code": "80320", "nom_comm": "HYPERCOURT"},
    {"insee_com": "26038", "postal_code": "26600", "nom_comm": "BEAUMONT MONTEUX"},
    {
        "insee_com": "28015",
        "postal_code": "28700",
        "nom_comm": "AUNEAU BLEURY SAINT SYMPHORIEN",
    },
    {"insee_com": "39043", "postal_code": "39190", "nom_comm": "BEAUFORT ORBAGNA"},
    {"insee_com": "02018", "postal_code": "02320", "nom_comm": "ANIZY LE GRAND"},
    {"insee_com": "49125", "postal_code": "49700", "nom_comm": "DOUE EN ANJOU"},
]
