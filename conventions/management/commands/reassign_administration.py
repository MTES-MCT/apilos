from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.management.base import BaseCommand, CommandParser
from django.db import models
from django.db.models import Q, QuerySet

from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Programme


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--departements",
            required=False,
            help="List of the impacted departements",
            action="store",
            nargs="+",
        )
        parser.add_argument(
            "--city-set",
            required=False,
            help="A named set of cities (ex: bordeaux, reims)",
            action="store",
            nargs="?",
        )
        parser.add_argument(
            "--new-admin-code",
            required=True,
            type=str,
            help="New administration to assign to the conventions (code)",
            action="store",
            nargs="?",
        )
        parser.add_argument(
            "--no-dry-run",
            default=False,
            action="store_true",
            help="Disable dry run mode",
        )
        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        self.stdout.write("Reassign administration command called")

        # Parse arguments
        departements = kwargs["departements"]
        city_set = kwargs["city_set"]
        new_admin = Administration.objects.get(code=kwargs["new_admin_code"])
        no_dry_run = kwargs["no_dry_run"]

        # Check arguments
        if not city_set and not departements:
            self.stdout.write(
                self.style.ERROR("You must provide either departements or a city-set")
            )
            return

        if city_set and departements:
            self.stdout.write(
                self.style.ERROR("You can't provide both departements and a city-set")
            )
            return

        if city_set:
            city_set = city_set.lower()
            if city_set not in city_sets:
                self.stdout.write(
                    self.style.ERROR(
                        f"Unknown city-set: {city_set}, available sets are: {city_sets.keys()}"
                    )
                )
                return

        # Find the conventions assigned to current_admin
        if departements:
            programmes = self._get_programme_qs_from_dpts(departements)
        elif city_set:
            programmes = self._get_programme_qs_from_city_set(city_set)
        else:  # unreachable
            programmes = Programme.objects.none()
        programmes = programmes.exclude(administration=new_admin)

        conventions = Convention.objects.filter(programme__in=programmes)

        old_admins = (
            programmes.values("administration")
            .distinct()
            .annotate(count=models.Count("pk"))
        )

        # Output summary
        self.stdout.write("Summary before execution:")
        self.stdout.write("--------------------------")
        programmes_count = programmes.count()
        self.stdout.write(f"{programmes_count} programmes will be updated:")
        if programmes_count < 10:
            for p in programmes:
                self.stdout.write(f"    - {p.nom} - {p.numero_operation}")
        self.stdout.write("--------------------------")
        conventions_count = conventions.count()
        self.stdout.write(f"{conventions_count} conventions will be impacted:")
        if conventions_count < 10:
            for c in conventions:
                self.stdout.write("    - " + str(c))
        self.stdout.write("--------------------------")
        self.stdout.write("Current administrations for the impacted conventions:")
        for old_admin in old_admins:
            admin = Administration.objects.get(pk=old_admin["administration"])
            self.stdout.write(f"{admin.code} ({old_admin['count']} conventions)")

        if no_dry_run:
            # Update administration and save history
            for p in programmes:
                p.reassign_command_old_admin_backup = {
                    "backup_code": p.administration.code
                }
                p.administration = new_admin
                p.save()
            self.stdout.write("Changes executed")
        else:
            self.stdout.write(self.style.WARNING("Dry run mode, no changes executed"))

    def _get_programme_qs_from_dpts(self, departements) -> QuerySet[Programme]:
        return Programme.objects.filter(code_insee_departement__in=departements)

    def _get_programme_qs_from_city_set(self, city_set) -> QuerySet[Programme]:
        queryset = Programme.objects.annotate(
            search_vector_ville=SearchVector("ville", config="french")
        )

        filters = Q()
        for item in city_sets.get(city_set, []):
            filters |= Q(
                code_postal__in=item["postal_codes"],
                search_vector_ville=SearchQuery(item["name"], config="french"),
            )

        return queryset.filter(filters)


city_sets = {
    "bordeaux": [
        {"postal_codes": [33440], "name": "Ambarès-et-Lagrave"},
        {"postal_codes": [33810], "name": "Ambès"},
        {"postal_codes": [33370], "name": "Artigues-près-Bordeaux"},
        {"postal_codes": [33530], "name": "Bassens"},
        {"postal_codes": [33130], "name": "Bègles"},
        {"postal_codes": [33290], "name": "Blanquefort"},
        {
            "postal_codes": [33000, 33100, 33200, 33300, 33800, 30072],
            "name": "Bordeaux",
        },
        {"postal_codes": [33270], "name": "Bouliac"},
        {"postal_codes": [33520], "name": "Bruges"},
        {"postal_codes": [33560], "name": "Carbon-Blanc"},
        {"postal_codes": [33150], "name": "Cenon"},
        {"postal_codes": [33320], "name": "Eysines"},
        {"postal_codes": [33270], "name": "Floirac"},
        {"postal_codes": [33170], "name": "Gradignan"},
        {"postal_codes": [33110], "name": "Le Bouscat"},
        {"postal_codes": [33185], "name": "Le Haillan"},
        {"postal_codes": [33320], "name": "Le Taillan-Médoc"},
        {"postal_codes": [33310], "name": "Lormont"},
        {"postal_codes": [33127], "name": "Martignas-sur-Jalle"},
        {"postal_codes": [33700], "name": "Mérignac"},
        {"postal_codes": [33290], "name": "Parempuyre"},
        {"postal_codes": [33600], "name": "Pessac"},
        {"postal_codes": [33160], "name": "Saint-Aubin-de-Médoc"},
        {"postal_codes": [33440], "name": "Saint-Louis-de-Montferrand"},
        {"postal_codes": [33160], "name": "Saint-Médard-en-Jalles"},
        {"postal_codes": [33440], "name": "Saint-Vincent-de-Paul"},
        {"postal_codes": [33400], "name": "Talence"},
        {"postal_codes": [33140], "name": "Villenave d’Ornon"},
    ],
    "reims": [
        {"postal_codes": [51700], "name": "Anthénay"},
        {"postal_codes": [51700], "name": "Anthénay"},
        {"postal_codes": [51700], "name": "Anthénay"},
        {"postal_codes": [51170], "name": "Aougny"},
        {"postal_codes": [51170], "name": "Arcis-le-Ponsart"},
        {"postal_codes": [51170], "name": "Arcis-le-Ponsart"},
        {"postal_codes": [51170], "name": "Arcis-le-Ponsart"},
        {"postal_codes": [51600], "name": "Auberive"},
        {"postal_codes": [51170], "name": "Aubilly"},
        {"postal_codes": [51110], "name": "Aumenancourt"},
        {"postal_codes": [51170], "name": "Baslieux-les-Fismes"},
        {"postal_codes": [51110], "name": "Bazancourt"},
        {"postal_codes": [51360], "name": "Beaumont-sur-Vesle"},
        {"postal_codes": [51490], "name": "Beine Nauroy"},
        {"postal_codes": [51220], "name": "Bermericourt"},
        {"postal_codes": [51420], "name": "Berru"},
        {"postal_codes": [51400], "name": "Betheniville"},
        {"postal_codes": [51430], "name": "Bezannes"},
        {"postal_codes": [51400], "name": "Billy-le-Grand"},
        {"postal_codes": [51170], "name": "Bligny"},
        {"postal_codes": [51390], "name": "Bouilly"},
        {"postal_codes": [51170], "name": "Bouleuse"},
        {"postal_codes": [51110], "name": "Boult-sur-Suippe"},
        {"postal_codes": [51110], "name": "Bourgogne-Fresne"},
        {"postal_codes": [51140], "name": "Bouvancourt"},
        {"postal_codes": [51400], "name": "Branscourt"},
        {"postal_codes": [51140], "name": "Breuil-sur-Vesle"},
        {"postal_codes": [51220], "name": "Brimont"},
        {"postal_codes": [51170], "name": "Brouillet"},
        {"postal_codes": [51430], "name": "Bétheny"},
        {"postal_codes": [51110], "name": "Caurel"},
        {"postal_codes": [51220], "name": "Cauroy-les-Hermonville"},
        {"postal_codes": [51430], "name": "Cernay-les-Reims"},
        {"postal_codes": [51140], "name": "Chalons-sur-Vesle"},
        {"postal_codes": [51170], "name": "Chambrecy"},
        {"postal_codes": [51500], "name": "Chamery"},
        {"postal_codes": [51500], "name": "Champfleury"},
        {"postal_codes": [51370], "name": "Champigny"},
        {"postal_codes": [51170], "name": "Chaumuzy"},
        {"postal_codes": [51140], "name": "Chenay"},
        {"postal_codes": [51500], "name": "Chigny-les-Roses"},
        {"postal_codes": [51220], "name": "Cormicy"},
        {"postal_codes": [51350], "name": "Cormontreuil"},
        {"postal_codes": [51390], "name": "Coulommes-la-Montagne"},
        {"postal_codes": [51140], "name": "Courcelles-Sapicourt"},
        {"postal_codes": [51220], "name": "Courcy"},
        {"postal_codes": [51170], "name": "Courlandon"},
        {"postal_codes": [51390], "name": "Courmas"},
        {"postal_codes": [51480], "name": "Courtagnon"},
        {"postal_codes": [51170], "name": "Courville"},
        {"postal_codes": [51170], "name": "Crugny"},
        {"postal_codes": [51700], "name": "Cuisles"},
        {"postal_codes": [51490], "name": "Dontrien"},
        {"postal_codes": [51500], "name": "Ecueil"},
        {"postal_codes": [51490], "name": "Epoye"},
        {"postal_codes": [51170], "name": "Faverolles-et-Coëmy"},
        {"postal_codes": [51170], "name": "Fismes"},
        {"postal_codes": [51390], "name": "Germigny"},
        {"postal_codes": [51390], "name": "Gueux"},
        {"postal_codes": [51220], "name": "Hermonville"},
        {"postal_codes": [51110], "name": "Heutregiville"},
        {"postal_codes": [51140], "name": "Hourges"},
        {"postal_codes": [51110], "name": "Isles-sur-Suippe"},
        {"postal_codes": [51390], "name": "Janvry"},
        {"postal_codes": [51140], "name": "Jonchery-sur-Vesle"},
        {"postal_codes": [51700], "name": "Jonquery"},
        {"postal_codes": [51390], "name": "Jouy-les-Reims"},
        {"postal_codes": [51170], "name": "Lagery"},
        {"postal_codes": [51110], "name": "Lavannes"},
        {"postal_codes": [51370], "name": "Les Mesneux"},
        {"postal_codes": [51400], "name": "Les-Petites-Loges"},
        {"postal_codes": [51170], "name": "Lhery"},
        {"postal_codes": [51220], "name": "Loivre"},
        {"postal_codes": [51500], "name": "Ludes"},
        {"postal_codes": [51170], "name": "Magneux"},
        {"postal_codes": [51500], "name": "Mailly-Champagne"},
        {"postal_codes": [51170], "name": "Marfaux"},
        {"postal_codes": [51220], "name": "Merfy"},
        {"postal_codes": [51390], "name": "Mery-Premecy"},
        {"postal_codes": [51170], "name": "Mont-sur-Courville"},
        {"postal_codes": [51500], "name": "Montbre"},
        {"postal_codes": [51140], "name": "Montigny-sur-Vesle"},
        {"postal_codes": [51140], "name": "Muizon"},
        {"postal_codes": [51420], "name": "Nogent-l'Abbesse"},
        {"postal_codes": [51700], "name": "Olizy-Violaine"},
        {"postal_codes": [51370], "name": "Ormes"},
        {"postal_codes": [51390], "name": "Pargny-les-Reims"},
        {"postal_codes": [51140], "name": "Pevy"},
        {"postal_codes": [51170], "name": "Poilly"},
        {"postal_codes": [51110], "name": "Pomacle"},
        {"postal_codes": [51490], "name": "Pontfaverger-Moronvilliers"},
        {"postal_codes": [51220], "name": "Pouillon"},
        {"postal_codes": [51480], "name": "Pourcy"},
        {"postal_codes": [51400], "name": "Prosnes"},
        {"postal_codes": [51140], "name": "Prouilly"},
        {"postal_codes": [51360], "name": "Prunay"},
        {"postal_codes": [51500], "name": "Puisieulx"},
        {"postal_codes": [51100, 51722], "name": "Reims"},
        {"postal_codes": [51100, 51722], "name": "Reims"},
        {"postal_codes": [51100, 51722], "name": "Reims"},
        {"postal_codes": [51500], "name": "Rilly-la-Montagne"},
        {"postal_codes": [51140], "name": "Romain"},
        {"postal_codes": [51170], "name": "Romigny"},
        {"postal_codes": [51390], "name": "Rosnay"},
        {"postal_codes": [51500], "name": "Sacy"},
        {"postal_codes": [51370], "name": "Saint-Brice-Courcelles"},
        {"postal_codes": [51110], "name": "Saint-Etienne-sur-Suippe"},
        {"postal_codes": [51390], "name": "Saint-Euphraise-et-Clairizet"},
        {"postal_codes": [51170], "name": "Saint-Gilles"},
        {"postal_codes": [51490], "name": "Saint-Hilaire-le-Petit"},
        {"postal_codes": [51500], "name": "Saint-Leonard"},
        {"postal_codes": [51110], "name": "Saint-Martin-l'Heureux"},
        {"postal_codes": [51490], "name": "Saint-Masmes"},
        {"postal_codes": [51600], "name": "Saint-Souplet-sur-Py"},
        {"postal_codes": [51220], "name": "Saint-Thierry"},
        {"postal_codes": [51170], "name": "Sarcy"},
        {"postal_codes": [51170], "name": "Savigny-sur-Ardres"},
        {"postal_codes": [51490], "name": "Selles"},
        {"postal_codes": [51400], "name": "Sept-Saulx"},
        {"postal_codes": [51500], "name": "Sermiers"},
        {"postal_codes": [51170], "name": "Serzy-et-Prin"},
        {"postal_codes": [51500], "name": "Sillery"},
        {"postal_codes": [51500], "name": "Taissy"},
        {"postal_codes": [51220], "name": "Thil"},
        {"postal_codes": [51370], "name": "Thillois"},
        {"postal_codes": [51370], "name": "Tinqueux"},
        {"postal_codes": [51170], "name": "Tramery"},
        {"postal_codes": [51380], "name": "Trepail"},
        {"postal_codes": [51140], "name": "Treslon"},
        {"postal_codes": [51140], "name": "Trigny"},
        {"postal_codes": [51500], "name": "Trois-Puits"},
        {"postal_codes": [51170], "name": "Unchair"},
        {"postal_codes": [51360], "name": "Val-de-Vesle"},
        {"postal_codes": [51140], "name": "Vandeuil"},
        {"postal_codes": [51380], "name": "Vaudemange"},
        {"postal_codes": [51600], "name": "Vaudesincourt"},
        {"postal_codes": [51140], "name": "Ventelay"},
        {"postal_codes": [51360], "name": "Verzenay"},
        {"postal_codes": [51380], "name": "Verzy"},
        {"postal_codes": [51500], "name": "Ville en Selve"},
        {"postal_codes": [51170], "name": "Ville-en-Tardenois"},
        {"postal_codes": [51390], "name": "Villedommange"},
        {"postal_codes": [51500], "name": "Villers-Allerand"},
        {"postal_codes": [51220], "name": "Villers-Franqueux"},
        {"postal_codes": [51380], "name": "Villers-Marmery"},
        {"postal_codes": [51500], "name": "Villers-aux-Noeuds"},
        {"postal_codes": [51390], "name": "Vrigny"},
        {"postal_codes": [51110], "name": "Warmeriville"},
        {"postal_codes": [51420], "name": "Witry-les-Reims"},
    ],
    "strasbourg": [
        {"postal_codes": [67204], "name": "Achenheim"},
        {"postal_codes": [67800], "name": "Bischheim"},
        {"postal_codes": [67113], "name": "Blaesheim"},
        {"postal_codes": [67112], "name": "Breuschwickersheim"},
        {"postal_codes": [67201], "name": "Eckbolsheim"},
        {"postal_codes": [67550], "name": "Eckwersheim"},
        {"postal_codes": [67960], "name": "Entzheim"},
        {"postal_codes": [67114], "name": "Eschau"},
        {"postal_codes": [67640], "name": "Fegersheim"},
        {"postal_codes": [67118], "name": "Geispolsheim"},
        {"postal_codes": [67980], "name": "Hangenbieten"},
        {"postal_codes": [67800], "name": "Hœnheim"},
        {"postal_codes": [67810], "name": "Holtzheim"},
        {"postal_codes": [67218], "name": "Illkirch-Graffenstaden"},
        {"postal_codes": [67120], "name": "Kolbsheim"},
        {"postal_codes": [67450], "name": "Lampertheim"},
        {"postal_codes": [67380], "name": "Lingolsheim"},
        {"postal_codes": [67640], "name": "Lipsheim"},
        {"postal_codes": [67206], "name": "Mittelhausbergen"},
        {"postal_codes": [67450], "name": "Mundolsheim"},
        {"postal_codes": [67207], "name": "Niederhausbergen"},
        {"postal_codes": [67205], "name": "Oberhausbergen"},
        {"postal_codes": [67203], "name": "Oberschaeffolsheim"},
        {"postal_codes": [67990], "name": "Osthoffen"},
        {"postal_codes": [67540], "name": "Ostwald"},
        {"postal_codes": [67115], "name": "Plobsheim"},
        {"postal_codes": [67116], "name": "Reichstett"},
        {"postal_codes": [67300], "name": "Schiltigheim"},
        {"postal_codes": [67460], "name": "Souffelweyersheim"},
        {"postal_codes": [67550], "name": "Vendenheim"},
        {"postal_codes": [67610], "name": "La Wantzenau"},
        {"postal_codes": [67202], "name": "Wolfisheim"},
    ],
}
