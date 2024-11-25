import csv
import re
from collections import defaultdict
from datetime import datetime

import requests
from django.core.management.base import BaseCommand

# URL de l'API GitHub pour les releases, commits et pull requests du projet
REPO_RELEASES_URL = "https://api.github.com/repos/MTES-MCT/apilos/releases"
REPO_COMMITS_URL = "https://api.github.com/repos/MTES-MCT/apilos/commits"
REPO_PULLS_URL = "https://api.github.com/repos/MTES-MCT/apilos/pulls"


# Dictionnaire pour stocker les statistiques de chaque mois
monthly_stats = defaultdict(
    lambda: {
        "major": 0,
        "minor": 0,
        "patch": 0,
        "total_commits": 0,
        "dependabot_commits": 0,
        "manual_commits": 0,
        "label_counts": defaultdict(int),  # Comptes des commits par label
    }
)


def get_tags_from_release(
    start_date: datetime, headers: dict
) -> tuple[list[dict], dict]:
    returned_releases = []
    previous_release = {}

    # Récupérer les releases et compter les types par mois
    response = requests.get(REPO_RELEASES_URL, headers=headers)
    releases = response.json()
    if response.status_code == 200:
        for release in releases:
            # Extraire la date de publication et le tag de la release
            release_date = datetime.strptime(
                release["published_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
            # Ajouter le tag à la liste si la date de publication est après start_date
            if release_date >= start_date:
                returned_releases.append(
                    {
                        "tag_name": release["tag_name"],
                        "published_at": release["published_at"],
                    }
                )
            else:
                # Mettre à jour le tag précédent si la date de publication est avant
                # start_date
                if not previous_release or release_date > datetime.strptime(
                    previous_release["published_at"], "%Y-%m-%dT%H:%M:%SZ"
                ):
                    previous_release = {
                        "tag_name": release["tag_name"],
                        "published_at": release["published_at"],
                    }

    else:
        error_message = response.json()
        raise Exception(
            f"Erreur: {response.status_code} : {
                error_message['message']
                if 'message' in error_message
                else response.json()
            }."
        )

    return returned_releases, previous_release


def get_release_stats(tags: list[dict]) -> dict[str, dict]:
    monthly_stats = defaultdict(
        lambda: {
            "major": 0,
            "minor": 0,
            "patch": 0,
        }
    )
    for tag in tags:
        tag_name = tag["tag_name"]
        tag_date = datetime.strptime(tag["published_at"], "%Y-%m-%dT%H:%M:%SZ")
        month_year = tag_date.strftime("%Y-%m")
        # Vérifier le format sémantique (par exemple : v1.2.3)
        if tag_name.startswith("v") and len(tag_name.split(".")) == 3:
            # Extraire les parties majeure, mineure et patch du tag
            major, minor, patch = tag_name[1:].split(".")
            major, minor, patch = int(major), int(minor), int(patch)

            # Incrémenter les compteurs en fonction du type de version
            if major > 0 and minor == 0 and patch == 0:
                monthly_stats[month_year]["major"] += 1
            elif minor > 0 and patch == 0:
                monthly_stats[month_year]["minor"] += 1
            elif patch > 0:
                monthly_stats[month_year]["patch"] += 1

    return monthly_stats


def get_tags_with_details(
    previous_tag: dict, tags: list[dict], headers: dict
) -> list[dict]:
    tags_with_details = []

    # Trier les tags par date de publication
    tags = tags + [previous_tag]
    tags = sorted(
        tags, key=lambda x: datetime.strptime(x["published_at"], "%Y-%m-%dT%H:%M:%SZ")
    )

    pr_pattern = re.compile(r"#(\d+)")

    for i in range(len(tags) - 1):
        tag1 = tags[i]
        tag2 = tags[i + 1]

        # Récupérer les commits entre les deux tags
        response = requests.get(
            REPO_COMMITS_URL,
            params={
                "sha": tag2["tag_name"],
                "since": tag1["published_at"],
                "until": tag2["published_at"],
                "per_page": 100,
            },
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(f"Erreur: {response.status_code} : {response.json()}")

        commits = response.json()
        prs = []
        labels_count = defaultdict(int)

        for commit in response.json():
            message = commit["commit"]["message"]
            pr_numbers = pr_pattern.findall(message)
            prs.extend(pr_numbers)

            # Récupérer les labels des PRs
            for pr_number in pr_numbers:
                pr_response = requests.get(
                    f"{REPO_PULLS_URL}/{pr_number}", headers=headers
                )
                if pr_response.status_code == 200:
                    pr_data = pr_response.json()
                    for label in pr_data["labels"]:
                        labels_count[label["name"]] += 1

        tag2["PRs"] = prs
        tag2["nb_commits"] = len(commits)
        tag2["labels_count"] = dict(labels_count)
        tags_with_details.append(tag2)

    return tags_with_details


def get_stats_by_month(
    tags_with_prs_and_nb_commits_and_labels: list[dict],
) -> dict[str, dict]:
    consolidation_par_mois = defaultdict(
        lambda: {"nb_commits": 0, "labels_count": defaultdict(int)}
    )

    for tag_info in tags_with_prs_and_nb_commits_and_labels:
        # Extraire la date de publication et convertir-la en mois et année
        published_at = tag_info["published_at"]
        mois_annee = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%Y-%m"
        )

        # Ajouter le nombre de commits
        consolidation_par_mois[mois_annee]["nb_commits"] += tag_info["nb_commits"]

        # Ajouter les labels
        for label, count in tag_info["labels_count"].items():
            consolidation_par_mois[mois_annee]["labels_count"][label] += count

    # Convertir les defaultdict en dict pour un affichage plus propre
    for _, data in consolidation_par_mois.items():
        data["labels_count"] = dict(data["labels_count"])

    return dict(consolidation_par_mois)


def flatten_labels_counts(tag_stats_by_month):
    # Obtenir tous les labels uniques
    all_labels = set()
    for stats in tag_stats_by_month.values():
        all_labels.update(stats["labels_count"].keys())

    # Créer une nouvelle structure de données avec les labels à plat
    flattened_stats = {}
    for month, stats in tag_stats_by_month.items():
        flattened_stats[month] = {"nb_commits": stats["nb_commits"]}
        for label in all_labels:
            flattened_stats[month][label] = stats["labels_count"].get(label, 0)

    return flattened_stats


def merge_dicts_by_month(tag_stats_by_month, release_stats_by_month):
    merged_stats = defaultdict(lambda: defaultdict(int))

    # Fusionner les stats des tags
    for month, stats in tag_stats_by_month.items():
        merged_stats[month].update(stats)

    # Fusionner les stats des releases
    for month, stats in release_stats_by_month.items():
        for key, value in stats.items():
            merged_stats[month][key] += value

    # Convertir les defaultdict en dict pour un affichage plus propre
    return {month: dict(stats) for month, stats in merged_stats.items()}


def exporter_dict_en_csv(data: dict[str, dict], fichier_csv: str) -> None:
    with open(fichier_csv, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Ordre spécifique des colonnes
        ordered_columns = [
            "major",
            "minor",
            "patch",
            "nb_commits",
            "enhancement",
            "bug",
            "technical",
            "dependencies",
            "escalation",
        ]

        # Obtenir toutes les colonnes existantes dans les données
        all_columns = set()
        for stats in data.values():
            all_columns.update(stats.keys())

        # Filtrer les colonnes dans l'ordre spécifié et ajouter les autres colonnes
        headers = (
            ["Mois-Annee"]
            + [col for col in ordered_columns if col in all_columns]
            + sorted(all_columns - set(ordered_columns))
        )
        writer.writerow(headers)

        # Écrire les données
        for mois_annee, stats in data.items():
            row = [mois_annee] + [stats.get(key, 0) for key in headers[1:]]
            writer.writerow(row)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--token",
            help="""
Les tokens doivent être créés manuellement dans les paramètres de compte GitHub pour
des raisons de sécurité : https://github.com/settings/tokens
Un token est nécessaire pour que la commande soit executée sans atteindre de limite.
""",
            required=True,
        )
        parser.add_argument(
            "--output",
            help="Nom du fichier CSV de sortie",
            default="consolidation_par_mois.csv",
        )
        parser.add_argument(
            "--start-date",
            help="Date de début pour filtrer les releases, commits et pull requests",
            default="2024-09-01",
        )

    def handle(self, *args, **options):
        start_date = datetime.strptime(options["start_date"], "%Y-%m-%d")
        headers = {"Authorization": f"token {options['token']}"}

        (tags, previous_tag) = get_tags_from_release(start_date, headers)

        tags_with_prs_and_nb_commits_and_labels = get_tags_with_details(
            previous_tag, tags, headers
        )

        tag_stats_by_month = get_stats_by_month(tags_with_prs_and_nb_commits_and_labels)
        tag_stats_by_month = flatten_labels_counts(tag_stats_by_month)
        release_stats_by_month = get_release_stats(tags)

        stats_by_month = merge_dicts_by_month(
            tag_stats_by_month, release_stats_by_month
        )

        exporter_dict_en_csv(stats_by_month, options["output"])

        self.stdout.write(
            self.style.SUCCESS(
                "Exportation terminée avec succès."
                f" Statistiques disponibles dans {options["output"]}"
            )
        )
