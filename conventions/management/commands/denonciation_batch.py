import datetime

from django.core.management.base import BaseCommand

from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from conventions.services.avenants import _get_last_avenant
from conventions.services.recapitulatif import convention_denonciation_validate
from users.models import User

numeros = [
    "25/3/12-1988/77-1019/247",
    "25/3/12-1988/80-429/246",
    "25/2/12-1988/80-429/245",
    "25/2/12-1988/80-429/242",
    "25/3/11-1988/77-1019/236",
    "25/3/11-1988/80-429/233",
    "25 D 4 1 89 12 361 0232",
    "25/3/12-1989/80-429/229",
    "25/3/12-1989/80-429/228",
    "25/2/11-1988/80-429/228",
    "25/2/12-1989/80-429/227",
    "25 D 4 1 89 12 361 0224",
    "25/3/11-1989/80-429/219",
    "25/3/11-1989/80-429/217",
    "25/3/10-1988/80-429/213",
    "25/3/10-1988/80-429/212",
    "25/3/10-1988/80-429/211",
    "25/3/10-1988/80-429/209",
    "25/3/10-1988/80-429/208",
    "25/3/09-1988/80-429/201",
    "25/2/09-1989/80-429/199",
    "25/2/09-1989/78-1307/198",
    "25/3/09-1988/80-429/197",
    "25/3/09-1988/77-948/193",
    "25/3/09-1989/77-1019/191",
    "25 D 4 1 88 07 S 0183",
    "25/3/07-1988/80-429/182",
    "25/2/07-1988/80-429/176",
    "25/3/07-1988/80-429/165",
    "25/3/12-1987/80-429/163",
    "25/2/07-1989/80-429/154",
    "25/2/07-1989/78-1307/148",
    "25/2/07-1989/80-429/146",
    "25/2/12-1990/80-429/146",
    "25/2/12-1990/80-429/145",
    "25/2/12-1990/80-429/144",
    "25/3/12-1993/80-429/143",
    "25 D 4 1 93 11 361 0141",
    "25/3/12-1987/80-429/139",
    "25/3/11-1993/80-429/138",
    "25/3/11-1993/80-429/137",
    "25/3/12-1991/77-1019/137",
    "25/2/10-1987/78-1307/136",
    "25/3/12-1990/80-429/136",
    "25/3/12-1994/80-429/135",
    "25/3/11-1987/80-429/135",
    "25/3/12-1990/80-429/135",
    "25/2/12-1990/80-429/134",
    "25/3/10-1996/80-429/133",
    "25/3/12-1994/80-429/132",
    "25/3/11-1994/77-1019/131",
    "25/3/12-1996/77-1019/130",
    "25 D 4 1 90 12 361 0128",
    "25/3/11-1994/77-1019/128",
    "25/2/10-1993/80-429/127",
    "25/2/06-1989/80-429/126",
    "25/2/10-1993/80-429/126",
    "25/3/11-1994/80-429/126",
    "25/2/06-1992/77-948/126",
    "25/3/06-1989/80-429/125",
    "25/2/12-1992/80-429/125",
    "25/3/11-1991/80-429/125",
    "25/3/11-1994/77-1019/125",
    "25/3/11-1987/78-1307/124",
    "25/3/11-1991/80-429/124",
    "25/3/12-1996/80-429/124",
    "25/3/10-1993/80-429/123",
    "25/3/10-1994/80-429/123",
    "25/3/06-1989/77-1019/121",
    "25/3/10-1994/80-429/120",
    "25/2/11-1990/77-1019/120",
    "25/3/06-1989/77-1019/120",
    "25/2/10-1990/80-429/119",
    "25/2/11-1987/83-1001/119",
    "25/2/07-1985/77-1019/118",
    "25 D 4 1 85 12 361 0115",
    "25/2/12-1997/80-429/115",
    "25/3/12-1985/77-948/113",
    "25/3/10-1987/80-429/113",
    "25/3/10-1987/80-429/112",
    "25/3/11-1996/80-429/112",
    "25/3/10-1994/77-1019/112",
    "25/2/09-1991/80-429/111",
    "25/3/10-1993/80-429/110",
    "25/2/10-1992/80-429/110",
    "25/2/09-1991/80-429/109",
    "25/3/11-1997/77-1019/109",
    "25 D 4 1 91 09 361 0108",
    "25/3/10-1994/80-429/108",
    "25/3/10-1987/80-429/107",
    "25/3/09-1991/80-429/107",
    "25/2/12-1999/80-429/107",
    "25/3/12-1998/80-429/106",
    "25/2/12-1985/80-429/105",
    "25/2/07-1987/80-429/104",
    "25/2/08-1990/80-429/104",
    "25 D 3 1 97 11 S 0104",
    "25/2/12-1985/80-429/104",
    "25 D 3 1 92 09 S 0104",
    "25/2/07-1987/80-429/103",
    "25/3/10-1994/80-429/103",
    "25/3/09-1993/77-1019/103",
    "25/3/10-1994/80-429/102",
    "25/2/12-1985/80-429/102",
    "25/2/07-1987/80-429/102",
    "25/3/12-1999/80-429/102",
    "25/3/10-1997/77-1019/102",
    "25/2/11-1998/80-429/101",
    "25/2/10-1985/80-429/101",
    "25/3/12-1999/80-429/101",
    "25/3/08-1990/77-1019/101",
    "25/3/11-1998/80-429/100",
    "25/2/10-1996/80-429/100",
    "25/2/11-1998/80-429/099",
    "25/3/10-1996/77-1019/099",
    "25/3/09-1991/77-1019/099",
    "25 D 3 1 92 09 361 0099",
    "25/3/10-1987/80-429/098",
    "25/3/09-1992/77-1019/098",
    "25/3/09-1993/77-1019/098",
    "25/3/09-1987/80-429/097",
    "25/3/09-1991/77-1019/097",
    "25/2/09-1991/80-429/096",
    "25 D 4 1 97 10 S 0096",
    "25/3/11-1986/80-429/096",
    "25/3/09-1993/80-429/095",
    "25/3/10-1997/80-429/095",
    "25/2/12-1983/80-429/095",
    "25 D 4 1 00 12 S 0095",
    "25/2/12-1984/77-948/095",
    "25/3/10-1996/80-429/094",
    "25/3/07-1990/77-948/094",
    "25/3/12-1983/80-429/093",
    "25/3/11-1985/80-429/093",
    "25/3/07-1990/77-948/093",
    "25/3/11-1986/80-429/092",
    "25/3/10-1999/80-429/092",
    "25/3/08-1991/77-1019/092",
    "25 D 4 1 00 12 S 0091",
    "25/3/10-1986/80-429/091",
    "25/3/08-1992/80-429/091",
    "25/3/10-1997/80-429/091",
    "25/3/10-1986/80-429/090",
    "25/3/10-1996/80-429/090",
    "25 D 4 1 93 09 361 0090",
    "25/3/10-1996/80-429/090",
    "25/3/10-1996/80-429/089",
    "25/3/08-1991/80-429/089",
    "25 D 4 1 00 12 S 0089",
    "25/3/08-1987/80-429/089",
    "25/2/09-1993/80-429/089",
    "25/3/10-1999/80-429/089",
    "25/3/10-1996/80-429/089",
    "25/3/10-1985/80-429/088",
    "25/3/08-1993/77-1019/088",
    "25/3/09-1986/80-429/087",
    "25/2/07-1991/80-429/087",
    "25/3/10-1999/80-429/087",
    "25/2/11-1995/80-429/087",
    "25/3/08-1992/80-429/086",
    "25/3/09-1987/80-429/086",
    "25/3/12-2000/80-429/086",
    "25/3/08-1992/80-429/085",
    "25/3/09-1998/80-429/085",
    "25 D 4 1 01 12 361 0085",
    "25/2/10-1984/80-429/084",
    "25/2/09-1985/78-1307/084",
    "25/3/11-2000/97-535/084",
    "25/3/09-1998/77-948/083",
    "25/2/11-1993/80-429/083",
    "25/2/09-1999/80-429/083",
    "25/3/08-1992/77-1019/083",
    "25/3/08-1993/80-429/082",
    "25/3/11-2000/97-535/082",
    "25/2/09-1996/80-429/081",
    "25/3/11-1995/80-429/081",
    "25 D 4 1 02 10 S 0081",
    "25/2/07-1994/80-429/080",
    "25/3/08-1993/80-429/080",
    "25 D 4 1 99 09 361 0080",
    "25/3/06-1988/77-1019/080",
    "25/3/11-2000/97-535/080",
    "25/3/10-1984/78-198/079",
    "25/3/09-1983/78-1307/079",
    "25/3/09-1999/80-429/079",
    "25/3/09-1983/78-1307/078",
    "25/3/07-1994/80-429/078",
    "25/3/09-1999/80-429/078",
    "25/3/08-1993/80-429/078",
    "25/3/09-1996/80-429/078",
    "25 D 4 1 04 12 361 0078",
    "25 D 4 1 04 12 361 0078",
    "25/3/09-1999/80-429/078",
    "25/2/07-1990/77-948/077",
    "25/2/08-1992/80-429/077",
    "25 D 4 1 02 10 S 0077",
    "25/3/08-1996/80-429/077",
    "25/3/09-1983/78-1307/076",
    "25/2/07-1991/80-429/076",
    "25/3/08-1987/80-429/076",
    "25/2/07-1990/77-948/076",
    "25/2/08-1993/78-1307/075",
    "25/3/07-1992/80-429/075",
    "25/3/11-2003/80-429/075",
    "25 D 3 1 87 08 S 0075",
    "25/3/07-1991/77-1019/075",
    "25/2/07-1990/77-1019/074",
    "25/3/06-1990/77-948/073",
    "25/3/08-1996/80-429/073",
    "25/2/06-1988/77-1019/073",
    "25/3/06-1990/77-948/072",
    "25/3/11-1985/80-429/072",
    "25/3/07-1991/80-429/072",
    "25 D 4 1 00 10 S 0072",
    "25 D 4 1 02 10 886 0072",
    "25/3/08-1997/80-429/072",
    "25/3/06-1994/77-1019/072",
    "25/3/07-1991/80-429/071",
    "25 D 4 1 02 10 S 0071",
    "25/3/07-1993/80-429/071",
    "25/2/06-1990/77-948/071",
    "25 D 4 1 04 09 S 0071",
    "25 D 4 1 03 10 S 0071",
    "25/3/07-1992/80-429/070",
    "25 D 4 1 94 06 886 0070",
    "25/3/07-1991/80-429/070",
    "25/3/10-2002/97-535/070",
    "25/3/12-2005/97-535/070",
    "25/3/05-1985/78-1307/069",
    "25/3/07-1983/78-1307/069",
    "25/3/08-1997/80-429/069",
    "25/2/06-1990/77-948/069",
    "25/2/10-1995/80-429/069",
    "25/3/10-2002/97-535/069",
    "25/2/06-1993/77-1019/069",
    "25/2/03-1989/80-429/068",
    "25/3/06-1994/80-429/068",
    "25 D 4 1 93 06 S 0068",
    "25/2/09-2002/80-429/068",
    "25/3/07-1991/77-1019/068",
    "25/3/07-1983/78-1307/067",
    "25/3/08-1998/80-429/067",
    "25/3/06-1994/77-1019/067",
    "25/3/09-1995/78-1307/066",
    "25/2/03-1989/78-1307/066",
    "25/3/07-1986/80-429/066",
    "25/2/10-2006/80-429/066",
    "25/3/09-1995/80-429/065",
    "25/3/07-1986/80-429/065",
    "25 D 3 1 98 08 S 0065",
    "25 D 3 1 97 05 S 0065",
    "25/3/06-1996/80-429/064",
    "25/3/11-2001/80-429/064",
    "25/3/12-1982/78-1307/063",
    "25/3/10-1986/80-429/063",
    "25/3/08-1997/80-429/063",
    "25/2/06-1996/80-429/063",
    "25 D 4 1 03 08 886 0063",
    "25/3/11-2001/80-429/063",
    "25 D 3 1 92 07 S 0063",
    "25 D 4 1 81 11 361 0062",
    "25/2/05-1990/77-948/062",
    "25 D 4 1 01 11 S 0062",
    "25/3/06-1996/80-429/062",
    "25 D 4 1 87 06 361 0061",
    "25/2/07-1984/80-429/061",
    "25/3/09-2000/80-429/061",
    "25/3/05-1985/80-429/061",
    "25 D 4 1 01 11 361 0061",
    "25 D 3 1 98 08 S 0061",
    "25/3/05-1997/77-1019/061",
    "25/2/03-1989/78-1307/060",
    "25/2/05-1994/80-429/060",
    "25/3/05-1993/80-429/060",
    "25/2/08-2002/80-429/060",
    "25/3/06-1983/77-1019/060",
    "25/3/08-1998/77-948/059",
    "25/3/11-1981/80-429/059",
    "25/3/07-1985/80-429/059",
    "25/3/05-1997/77-1019/059",
    "25/3/08-2006/97-535/059",
    "25/2/03-1989/78-1307/058",
    "25/3/05-1987/80-429/058",
    "25/2/06-1984/80-429/057",
    "25 D 3 1 85 07 S 0057",
    "25/2/05-1993/80-429/057",
    "25/3/06-1988/80-429/057",
    "25 D 4 1 01 10 S 0057",
    "25 D 4 1 03 08 S 0057",
    "25/2/08-1998/80-429/057",
    "25/3/08-2006/80-429/057",
    "25/2/03-1989/80-429/056",
    "25/2/05-1996/80-429/056",
    "25 D 4 1 01 09 S 0056",
    "25 D 4 1 02 07 361 0056",
    "25/3/08-2003/80-429/056",
    "25 D 3 1 90 05 S 0055",
    "25/3/07-2003/80-429/055",
    "25/3/06-1988/80-429/055",
    "25/3/11-2005/80-429/1/055",
    "25/3/07-2002/80-429/055",
    "25/3/08-1998/80-429/055",
    "25/3/06-1991/77-1019/055",
    "25/3/07-1985/77-1019/055",
    "25 D 3 1 92 07 S 0054",
    "25/2/10-1981/80-429/054",
    "25/2/06-2004/80-429/054",
    "25/3/05-1996/80-429/054",
    "25 D 4 1 98 07 886 0054",
    "25/2/06-2004/80-429/054",
    "25/3/07-2006/97-535/054",
    "25 D 3 1 00 07 S 0054",
    "25/3/05-1987/80-429/053",
    "25/3/06-1997/80-429/053",
    "25/3/06-1988/80-429/053",
    "25/2/05-1990/80-429/053",
    "25/3/06-1997/80-429/053",
    "25/3/04-1996/80-429/053",
    "25/3/11-1982/77-1019/053",
    "25/3/06-1991/77-1019/053",
    "25/3/05-1987/80-429/052",
    "25/3/05-1988/80-429/052",
    "25/2/05-1986/80-429/052",
    "25/3/07-2003/80-429/052",
    "25/2/06-1997/80-429/052",
    "25/3/06-2004/80-429/052",
    "25/3/06-1991/77-1019/052",
    "25 D 3 1 00 07 S 0052",
    "25 D 4 1 86 06 886 0051",
    "25 D 4 1 04 06 S 0051",
    "25/2/08-2001/80-429/051",
    "25/3/12-1980/78-198/1/050",
    "25/3/04-1996/80-429/050",
    "25/3/07-2006/97-535/050",
    "25/3/04-1993/78-1307/049",
    "25/3/06-1999/80-429/049",
    "25/3/05-1990/80-429/049",
    "25/2/07-2002/80-429/049",
    "25 D 4 1 01 07 361 0049",
    "25/3/06-2000/80-429/049",
    "25/3/07-2006/97-535/049",
    "25/3/05-1984/77-1019/049",
    "25/2/06-1991/77-1019/049",
    "25/3/05-1998/77-1019/049",
    "25/2/04-1987/79-297/048",
    "25/2/05.1984/80.429/048",
    "25/3/06-1986/80-429/048",
    "25/3/06-1991/80-429/048",
    "25/2/04-1988/80-429/048",
    "25/2/06-1999/80-429/048",
    "25 D 4 1 00 06 S 0048",
    "25/3/06-1992/80-429/047",
    "25/3/06-1999/80-429/047",
    "25/3/04-1993/80-429/047",
    "25/3/06-1999/80-429/047",
    "25 D 4 1 00 06 S 0047",
    "25/3/06-2004/97-535/047",
    "25/3/05-1984/78-198/046",
    "25/3/10-2005/80-429/046",
    "25/3/07-2006/80-429/046",
    "25/3/04-1988/80-429/045",
    "25/3/05-1992/80-429/045",
    "25/2/05-1997/80-429/045",
    "25/2/09-1981/80-429/044",
    "25/2/06-1991/80-429/044",
    "25 D 4 1 90 04 361 0044",
    "25 D 4 1 04 06 361 0044",
    "25/3/05-1992/80-429/044",
    "25/2/05-1984/80-429/044",
    "25 D 4 1 03 06 361 0044",
    "25 D 4 1 01 07 361 0044",
    "25 D 3 1 09 09 S 0044",
    "25/3/06-2003/80-429/043",
    "25/3/05-1984/80-429/043",
    "25/3/10-1982/80-429/043",
    "25/3/03-1994/80-429/043",
    "25 D 4 1 01 07 S 0043",
    "25/2/11-1980/80-429/042",
    "25/3/09-1982/80-429/042",
    "25 D 3 1 03 06 886 0042",
    "25/3/04-1990/77-1019/042",
    "25/3/06-2000/77-1019/042",
    "25 D 2 1 99 06 S 0042",
    "25/3/05-1984/78-1307/041",
    "25 D 4 1 92 05 S 0041",
    "25/3/09-1982/80-429/041",
    "25/2/04-1990/80-429/041",
    "25/3/06-1995/80-429/041",
    "25/2/03-1996/80-429/041",
    "25 D 4 1 03 06 S 0041",
    "25 D 4 1 03 06 S 0041",
    "25/3/04-1987/77-1019/041",
    "25/3/05-1997/77-1019/041",
    "25/3/05-1997/80-429/040",
    "25/2/05-1991/80-429/040",
    "25/3/05-1995/80-429/040",
    "25/3/03-1987/80-429/040",
    "25 D 4 1 86 05 886 0039",
    "25/2/03-1996/80-429/039",
    "25 D 4 1 88 04 361 0039",
    "25/3/04-1990/80-429/039",
    "25/2/05-1998/80-429/039",
    "25/3/05-1997/80-429/039",
    "25/3/05-1984/80-429/039",
    "25/3/07-2001/80-429/039",
    "25/3/05-1991/80-429/038",
    "25/2/07-1981/80-429/1/038",
    "25/3/04-1990/80-429/038",
    "25/3/08-2005/80-429/038",
    "25 D 4 1 02 06 S 0038",
    "25/2/06-2001/80-429/038",
    "25/2/04-1992/80-429/037",
    "25 D 4 1 00 04 S 0037",
    "25/3/03-1994/80-429/037",
    "25 D 4 1 00 04 S 0037",
    "25/3/05-2004/97-535/037",
    "25/3/04-1990/77-1019/037",
    "25/3/04-1988/80-429/036",
    "25/2/10-1980/80-429/036",
    "25 D 4 1 02 06 361 0036",
    "25/3/06-1999/77-948/035",
    "25/2/04-1983/80-429/035",
    "25 D 4 1 81 06 361 0035",
    "25/3/03-1996/80-429/035",
    "25 D 4 1 02 06 S 0035",
    "25/3/04-1998/77-1019/035",
    "25/3/06-2001/97-535/035",
    "25/3/05-2006/80-429/034",
    "25/2/05-1983/80-429/034",
    "25/2/02-1989/80-429/034",
    "25/3/04-1992/77-1019/034",
    "25/2/06-2003/01-207/034",
    "25/2/06-1981/80-429/033",
    "25 D 4 1 90 04 361 0033",
    "25/2/03-1987/80-429/033",
    "25/3/05-1995/80-429/033",
    "25/3/04-1991/77-1019/033",
    "25/3/05-1986/78-1307/032",
    "25/3/04-1990/80-429/032",
    "25/3/03-1987/80-429/032",
    "25/2/10-1980/80-429/032",
    "25/3/07-2005/97-535/032",
    "25 D 2 1 84 03 S 0032",
    "25/2/05-1985/79-297/031",
    "25/2/04-1990/80-429/031",
    "25 D 4 1 92 04 361 0031",
    "25/3/07-1982/80-429/031",
    "25/3/03-2000/80-429/031",
    "25/3/05-1995/77-1019/031",
    "25 D 3 1 93 03 S 0031",
    "25/3/03-1994/77-1019/031",
    "25/3/04-1998/80-429/030",
    "25 D 3 1 89 02 S 0030",
    "25/3/03-2000/80-429/030",
    "25 D 4 1 01 05 S 0030",
    "25/3/05-1995/80-429/030",
    "25/3/03-1983/80-429/030",
    "25/3/05-1981/80-429/1/030",
    "25/3/03-1997/80-429/030",
    "25 D 4 1 98 04 S 0029",
    "25/2/06-1982/80-429/029",
    "25 D 4 1 03 05 361 0029",
    "25/2/05-1995/80-429/029",
    "25 D 4 1 03 05 361 0029",
    "25/3/03-1993/77-1019/029",
    "25/3/06-1982/78-1307/028",
    "25/3/05-1986/80-429/028",
    "25/2/03-1990/80-429/028",
    "25/3/04-1991/80-429/028",
    "25/3/04-1988/80-429/028",
    "25/3/03-2006/80-429/028",
    "25/2/06-1986/80-429/027",
    "25/2/03-1990/80-429/027",
    "25/3/03-2000/80-429/027",
    "25/2/05-1981/80-429/027",
    "25/3/07-2005/80-429/027",
    "25/2/05-2002/80-429/027",
    "25/3/06-1982/78-198/027",
    "25/2/01-1989/78-1307/026",
    "25/3/10-1980/78-1307/026",
    "25 D 4 1 87 03 S 0026",
    "25/3/03-2006/80-429/026",
    "25 D 4 1 02 05 S 0026",
    "25/2/10-1980/80-429/025",
    "25/3/05-1999/80-429/025",
    "25/2/07-1982/80-429/025",
    "25/3/03-1990/77-1019/025",
    "25/3/03-1998/77-1019/025",
    "25/3/03-1984/78-198/024",
    "25/3/02-1987/80-429/024",
    "25/2/04-2001/80-429/024",
    "25/3/04-1986/80-429/024",
    "25/3/04-1992/77-1019/024",
    "25/3/05-1999/77-948/023",
    "25/3/09-1980/78-1307/023",
    "25/3/04-1986/80-429/023",
    "25 D 4 1 00 03 S 0023",
    "25/3/03-1990/80-429/023",
    "25/2/05-1982/80-429/023",
    "25/2/02-1987/80-429/023",
    "25 D 4 1 88 04 361 0022",
    "25/3/03-1987/80-429/022",
    "25/2/04-2001/80-429/022",
    "25/3/02-1984/80-429/022",
    "25/3/02-1997/77-948/022",
    "25/3/05-2003/80-429/022",
    "25/3/02-1987/80-429/021",
    "25 D 4 1 01 04 361 0021",
    "25 D 3 1 09 05 S 0021",
    "25 D 3 1 94 02 S 0021",
    "25/C/02-2006/80-429/020",
    "25/3/02-2000/80-429/020",
    "25 D 3 1 95 04 S 0020",
    "25/3/03-1983/77-1019/020",
    "25/3/05-1982/78-198/019",
    "25 D 4 1 04 03 361 0019",
    "25/3/02-2000/80-429/019",
    "25/3/09-1980/78-1307/019",
    "25/2/02-1990/80-429/019",
    "25/2/02-1996/80-429/019",
    "25 D 4 1 04 03 361 0019",
    "25/3/03-1985/77-948/019",
    "25/3/03-1987/77-1019/019",
    "25/3/04-1992/80-429/018",
    "25/2/02-2006/80-429/018",
    "25/3/03-1985/80-429/018",
    "25/3/03-2002/80-429/018",
    "25/2/05-1982/80-429/018",
    "25/2/02-1990/80-429/018",
    "25/2/02-2006/80-429/018",
    "25/3/03-2004/80-429/018",
    "25/3/05-1999/80-429/018",
    "25/3/02-1991/77-948/017",
    "25/3/05-1982/78-1307/017",
    "25 D 4 1 92 04 361 0017",
    "25/2/01-1996/80-429/017",
    "25/3/02-1994/80-429/017",
    "25/3/02-2000/80-429/017",
    "25/3/03-1985/80-429/016",
    "25/3/04-1999/80-429/016",
    "25/2/04-1981/80-429/016",
    "25 D 4 1 00 02 S 0016",
    "25/3/02-1994/80-429/016",
    "25 D 3 1 90 02 S 0016",
    "25/3/03-1992/77-1019/016",
    "25/3/02-1983/80-429/015",
    "25 D 4 1 00 02 S 0015",
    "25/2/02-1991/80-429/015",
    "25 D 4 1 95 04 S 0015",
    "25/2/02-1990/80-429/015",
    "25/2/05-1981/80-429/015",
    "25/3/02-1994/80-429/015",
    "25 D 4 1 02 03 S 0015",
    "25 D 4 1 01 03 361 0015",
    "25 D 4 1 03 02 S 0014",
    "25/3/02-1994/80-429/014",
    "25/3/03-1987/80-429/014",
    "25/3/04-1995/80-429/014",
    "25/3/02-2000/80-429/014",
    "25 D 4 1 03 02 S 0014",
    "25 D 4 1 01 03 S 0014",
    "25/3/03-1985/78-1307/013",
    "25/3/04-1982/80-429/013",
    "25 D 4 1 03 02 S 0013",
    "25 D 4 1 01 03 S 0013",
    "25/3/03-2002/80-429/013",
    "25/2/04-1982/78-1307/1/012",
    "25/3/02-1988/80-429/012",
    "25/3/02-1987/80-429/012",
    "25/3/03-1985/80-429/012",
    "25/3/02-2000/80-429/012",
    "25/3/03-2001/80-429/012",
    "25/3/03-1995/77-1019/012",
    "25/3/04-1985/78-1307/011",
    "25/3/01-1990/77-1019/011",
    "25/3/02-1983/80-429/011",
    "25 D 4 1 01 03 S 0011",
    "25/2/02-1983/78-1307/010",
    "25/2/01.1985/80-429/010",
    "25/3/02-1988/80-429/010",
    "25/3/01-1994/77-1019/010",
    "25/3/03-1992/80-429/009",
    "25/3/04-1999/80-429/009",
    "25 D 3 3 00 01 886 0009",
    "25/3/02-1993/77-1019/009",
    "25/2/04-1980/77-1131/008",
    "25/3/03-1982/80-429/008",
    "25/3/01-1986/80-429/008",
    "25/3/04-1999/80-429/008",
    "25/2/03-1982/80-429/007",
    "25/2/01-1996/80-429/007",
    "25/3/02-1993/80-429/007",
    "25/2/04-1980/77-1131/007",
    "25/2/02-1997/80-429/007",
    "25/3/01-1989/77-1019/007",
    "25/2/04-1981/80-429/006",
    "25/3/02-1997/80-429/006",
    "25/2/02-1999/80-429/006",
    "25/3/01-1986/80-429/006",
    "25/2/02-1987/80-429/006",
    "25/3/02-1997/80-429/006",
    "25/3/01-1989/77-1019/006",
    "25/3/02-1992/77-1019/006",
    "25/3/02-1988/80-429/005",
    "25/2/01-1990/80-429/005",
    "25/3/02-1995/80-429/005",
    "25/3/02-1999/80-429/005",
    "25 D 4 1 98 01 361 0005",
    "25/2/01-2000/80-429/005",
    "25/3/02-1992/77-1019/005",
    "25/2/01-1983/78-1307/004",
    "25/3/01-1985/80-429/004",
    "25/2/02-1981/80-429/004",
    "25/2/03-1982/80-429/004",
    "25/2/01-1993/80-429/004",
    "25/3/03-1980/77-1131/004",
    "25 D 4 1 06 01 361 0004",
    "25/3/01-1986/77-1019/004",
    "25/3/01-1984/80-429/003",
    "25/2/01-1993/80-429/003",
    "25 D 4 1 04 02 361 0003",
    "25 D 4 1 97 01 361 0003",
    "25/3/02-1985/77-1019/003",
    "25/2/01-1990/80-429/002",
    "25/3/02-1981/80-429/02",
    "25/3/01-1992/80-429/002",
    "25/3/02-1996/80-429/002",
    "25/3/01-1988/77-948/001",
    "25/2/01-1985/78-1307/001",
    "25/3/01-1999/80-429/001",
    "25/3/01-2000/80-429/001",
    "25/2/01-1993/80-429/001",
    "25/3/01-2003/80-429/001",
    "25/2/01-1981/80-429/01",
    "25 D 4 1 04 01 S 0001",
    "25/3/01-2003/80-429/001",
    "25/3/03-2001/80-429/001",
    "25 D 4 1 02 02 886 0001",
]

dates = [
    "30/12/2020",
    "30/12/2015",
    "30/06/1998",
    "30/06/2004",
    "01/07/1997",
    "12/12/2014",
    "20/12/2011",
    "28/12/2018",
    "30/06/2005",
    "30/06/2004",
    "30/06/2000",
    "30/06/2014",
    "30/06/1998",
    "30/06/2008",
    "30/06/2003",
    "30/06/2003",
    "30/06/2003",
    "30/06/2003",
    "30/06/2003",
    "28/12/2021",
    "30/06/1998",
    "06/07/2017",
    "30/06/2000",
    "08/12/2016",
    "15/10/1993",
    "12/11/2009",
    "30/06/2007",
    "30/06/2001",
    "30/06/2003",
    "30/06/2003",
    "30/06/1999",
    "30/06/2005",
    "21/12/2021",
    "30/06/2006",
    "30/06/2005",
    "30/06/2000",
    "30/06/2003",
    "20/12/2011",
    "30/06/1997",
    "30/06/2003",
    "30/06/2003",
    "20/12/2018",
    "30/06/2002",
    "30/06/2000",
    "30/06/2004",
    "29/11/2017",
    "16/12/2014",
    "30/06/2006",
    "30/06/2006",
    "30/06/2010",
    "13/06/2006",
    "14/12/2020",
    "03/07/2014",
    "23/12/2020",
    "30/06/2003",
    "30/06/2007",
    "30/06/2003",
    "30/06/2004",
    "10/05/2006",
    "30/06/2004",
    "30/06/2002",
    "30/06/2004",
    "26/11/2021",
    "21/06/2016",
    "30/06/2010",
    "30/06/2007",
    "30/06/2006",
    "30/06/2009",
    "05/11/2021",
    "30/06/2007",
    "30/06/2009",
    "04/01/2013",
    "14/11/2017",
    "30/08/2007",
    "07/02/2023",
    "26/04/2011",
    "30/06/2007",
    "29/12/2004",
    "30/06/1996",
    "30/06/1996",
    "30/06/2009",
    "23/12/2020",
    "30/06/2007",
    "30/06/2005",
    "30/06/2005",
    "30/06/2004",
    "02/05/2016",
    "03/12/2012",
    "03/11/2017",
    "30/06/1996",
    "30/06/2004",
    "30/06/2009",
    "30/06/2008",
    "30/06/2004",
    "30/06/1997",
    "30/06/2009",
    "28/03/2011",
    "30/06/2004",
    "25/11/2010",
    "30/06/2000",
    "30/06/2006",
    "30/06/2008",
    "30/06/2004",
    "30/06/2004",
    "30/06/1997",
    "22/12/2017",
    "26/10/2015",
    "30/06/2008",
    "30/06/2005",
    "28/12/2017",
    "30/06/2008",
    "30/06/2008",
    "30/06/2006",
    "30/06/2008",
    "29/11/2017",
    "30/06/2010",
    "20/12/2013",
    "30/06/1996",
    "21/04/2015",
    "04/01/2013",
    "30/06/2002",
    "26/10/2015",
    "30/06/2003",
    "06/11/2009",
    "30/06/2002",
    "30/06/2003",
    "24/12/2015",
    "27/12/2019",
    "23/12/2009",
    "13/06/2017",
    "30/06/2006",
    "30/06/2003",
    "26/12/2018",
    "30/06/1997",
    "30/06/2006",
    "30/06/2008",
    "30/06/2009",
    "27/12/2018",
    "31/10/2012",
    "30/06/2007",
    "30/06/2005",
    "30/06/2007",
    "30/06/2004",
    "30/06/2008",
    "19/10/2011",
    "30/06/2008",
    "30/06/2008",
    "30/06/2007",
    "10/12/2009",
    "30/06/2011",
    "31/12/2014",
    "30/06/2009",
    "30/06/2008",
    "30/06/2001",
    "21/09/2015",
    "30/06/2002",
    "30/06/2001",
    "30/06/2009",
    "30/06/2005",
    "12/09/2014",
    "30/06/2008",
    "30/06/2010",
    "30/06/2002",
    "30/06/2008",
    "16/12/2013",
    "30/06/2006",
    "30/06/2001",
    "20/12/2018",
    "18/06/2012",
    "30/06/2003",
    "30/06/2008",
    "30/06/2002",
    "30/06/2003",
    "27/12/2018",
    "30/06/2006",
    "30/06/2008",
    "06/12/2011",
    "30/06/2007",
    "30/06/2003",
    "07/06/2011",
    "30/06/2005",
    "23/12/2015",
    "30/12/2010",
    "30/06/2002",
    "30/12/2014",
    "30/06/2002",
    "30/06/2003",
    "05/12/2014",
    "30/06/2003",
    "30/06/2006",
    "09/12/2010",
    "09/12/2010",
    "05/12/2014",
    "30/06/2005",
    "30/06/2005",
    "15/11/2011",
    "30/06/2006",
    "30/06/2002",
    "30/06/2006",
    "30/06/1996",
    "30/06/2011",
    "30/06/2008",
    "19/12/2016",
    "29/12/2015",
    "17/12/2010",
    "28/10/2015",
    "30/06/2008",
    "30/06/2005",
    "30/06/2005",
    "30/06/2005",
    "30/06/2005",
    "30/06/2007",
    "30/06/2006",
    "28/12/2009",
    "27/12/2011",
    "30/06/2007",
    "21/06/2018",
    "30/06/2004",
    "15/11/2011",
    "30/06/2002",
    "30/06/2003",
    "30/12/2013",
    "31/12/2012",
    "30/06/2005",
    "04/01/2013",
    "28/12/2018",
    "22/12/2017",
    "28/12/2017",
    "30/06/1995",
    "30/06/1999",
    "30/06/2007",
    "30/06/2003",
    "13/12/2014",
    "22/12/2020",
    "30/06/2007",
    "30/06/2002",
    "30/06/2006",
    "20/12/2013",
    "21/12/2017",
    "12/12/2018",
    "30/06/1996",
    "19/12/2016",
    "30/06/2007",
    "30/06/2010",
    "30/06/2007",
    "04/09/2015",
    "01/10/2015",
    "30/06/2005",
    "30/06/2004",
    "11/12/2013",
    "10/11/2011",
    "22/12/2016",
    "30/06/2011",
    "30/06/1998",
    "30/06/2004",
    "30/06/2006",
    "30/06/2005",
    "30/06/2011",
    "22/12/2016",
    "16/02/2011",
    "04/03/2014",
    "30/06/1999",
    "08/12/2010",
    "30/06/2005",
    "22/11/2013",
    "30/06/2003",
    "19/05/2018",
    "30/06/1995",
    "28/12/2010",
    "13/12/2011",
    "30/06/2001",
    "30/06/2003",
    "30/06/2003",
    "30/06/2002",
    "29/12/2014",
    "30/06/2005",
    "01/01/2005",
    "30/06/1997",
    "30/06/1995",
    "30/06/2010",
    "02/09/2020",
    "30/06/2002",
    "30/06/2002",
    "30/06/2008",
    "29/12/2011",
    "30/06/2005",
    "30/06/2000",
    "01/07/2012",
    "20/12/2012",
    "30/06/2008",
    "05/12/2018",
    "30/06/2000",
    "30/06/2006",
    "30/12/2010",
    "23/12/2011",
    "10/09/2013",
    "29/12/2011",
    "21/10/2021",
    "30/06/1997",
    "21/12/2017",
    "02/03/2016",
    "30/06/2008",
    "29/12/2021",
    "14/12/2021",
    "28/11/2012",
    "30/06/2003",
    "29/12/2015",
    "30/06/2005",
    "27/12/2010",
    "29/12/2015",
    "22/12/2020",
    "30/10/2012",
    "30/06/1999",
    "30/06/2006",
    "30/06/2006",
    "30/06/2002",
    "30/06/2006",
    "30/06/2005",
    "02/01/2020",
    "18/12/2015",
    "30/06/1999",
    "30/06/1997",
    "30/06/2004",
    "19/03/2014",
    "30/06/2007",
    "02/11/2018",
    "14/06/2021",
    "22/03/2014",
    "27/12/2012",
    "26/11/2013",
    "30/06/2011",
    "30/06/1999",
    "30/06/2005",
    "22/12/2020",
    "30/06/2008",
    "04/02/2010",
    "30/06/2002",
    "21/12/2017",
    "19/12/2011",
    "17/11/2009",
    "22/12/2020",
    "30/06/2009",
    "30/06/2007",
    "30/03/2016",
    "30/06/2007",
    "30/06/2002",
    "22/02/2016",
    "30/06/2009",
    "30/06/1998",
    "30/06/2009",
    "14/02/2013",
    "30/06/2005",
    "30/06/2009",
    "30/06/2005",
    "30/06/2009",
    "23/12/2009",
    "15/11/2018",
    "30/06/2009",
    "29/12/2014",
    "17/12/2015",
    "06/11/2009",
    "30/06/2004",
    "30/06/2007",
    "30/06/1993",
    "30/06/2007",
    "10/10/2013",
    "21/12/2012",
    "30/06/2007",
    "30/06/1999",
    "23/12/2011",
    "18/11/2011",
    "29/12/2021",
    "15/12/2020",
    "30/06/2002",
    "30/06/1994",
    "30/06/2003",
    "29/12/2009",
    "30/06/1993",
    "22/12/1997",
    "14/11/2011",
    "30/06/2008",
    "03/12/2018",
    "23/12/2013",
    "30/06/2005",
    "09/11/2012",
    "30/06/2006",
    "30/06/2008",
    "30/06/2008",
    "05/10/2007",
    "09/11/2012",
    "09/11/2012",
    "30/06/2009",
    "30/06/2010",
    "30/06/2010",
    "30/06/2001",
    "30/06/2004",
    "30/06/2002",
    "10/12/2010",
    "30/06/2005",
    "20/12/2013",
    "30/06/2005",
    "30/06/2007",
    "30/06/2010",
    "30/06/2002",
    "06/07/2015",
    "30/06/2007",
    "30/06/1993",
    "30/06/2002",
    "28/12/2017",
    "03/11/2010",
    "30/06/2010",
    "30/06/2004",
    "19/12/2011",
    "30/06/2006",
    "19/12/2011",
    "20/12/2018",
    "20/12/2018",
    "30/06/2006",
    "30/06/1990",
    "09/12/2010",
    "28/01/2013",
    "30/03/1998",
    "31/05/2011",
    "30/06/2008",
    "21/12/2010",
    "21/12/2018",
    "15/12/2021",
    "21/12/2017",
    "30/06/2004",
    "30/06/2004",
    "29/12/2021",
    "26/12/2017",
    "30/06/1990",
    "06/05/2014",
    "30/06/2002",
    "30/06/2010",
    "30/06/2007",
    "30/06/2004",
    "30/06/2008",
    "30/06/2002",
    "30/06/1995",
    "02/10/2018",
    "22/07/2011",
    "14/02/2019",
    "30/06/2008",
    "29/11/2012",
    "30/06/2008",
    "30/06/2009",
    "30/06/2005",
    "17/12/2010",
    "13/06/2018",
    "30/06/2007",
    "29/12/2011",
    "24/12/2014",
    "18/12/2009",
    "30/06/2008",
    "22/09/1994",
    "30/06/1990",
    "30/06/2006",
    "30/12/2009",
    "30/06/1991",
    "27/12/2011",
    "30/06/2007",
    "27/12/2011",
    "03/11/2016",
    "30/06/1991",
    "30/06/2010",
    "30/06/2005",
    "30/06/2001",
    "30/06/2003",
    "31/12/2014",
    "30/06/2002",
    "30/06/2000",
    "30/06/2009",
    "30/06/1990",
    "20/12/2016",
    "26/12/2019",
    "05/11/2015",
    "30/06/2005",
    "30/06/2008",
    "21/05/2012",
    "10/12/2020",
    "04/12/2013",
    "30/06/1999",
    "30/06/2008",
    "30/06/1994",
    "28/12/2015",
    "30/06/2010",
    "30/06/2003",
    "30/06/2005",
    "30/06/2010",
    "30/06/2001",
    "16/11/2021",
    "16/01/2012",
    "30/06/1999",
    "30/06/2001",
    "02/03/2011",
    "30/06/2005",
    "30/06/1991",
    "30/06/2005",
    "30/06/2013",
    "30/06/2002",
    "30/06/2010",
    "30/06/1997",
    "30/06/2007",
    "27/11/2017",
    "30/06/2005",
    "18/12/2009",
    "07/12/2020",
    "20/12/2011",
    "22/12/2017",
    "30/06/2009",
    "17/12/2012",
    "26/11/2021",
    "30/06/2007",
    "04/10/2012",
    "30/06/2009",
    "30/06/2003",
    "30/06/2002",
    "30/06/2005",
    "04/10/2012",
    "29/10/2021",
    "30/06/2003",
    "30/06/2004",
    "21/12/2017",
    "30/06/1994",
    "19/12/2019",
    "30/06/1991",
    "30/06/2005",
    "21/12/2017",
    "21/12/2015",
    "28/08/2015",
    "27/07/2016",
    "30/06/1994",
    "22/12/2000",
    "30/06/2005",
    "30/06/2009",
    "30/06/2009",
    "30/06/1994",
    "30/06/2009",
    "30/06/2011",
    "08/12/2009",
    "30/06/2009",
    "08/08/2013",
    "27/12/2018",
    "30/06/2004",
    "17/12/2011",
    "03/03/2021",
    "30/10/2013",
    "26/12/2019",
    "30/06/1994",
    "30/06/2007",
    "17/12/2010",
    "29/11/2012",
    "12/12/2011",
    "30/06/2009",
    "30/06/2008",
    "30/06/2004",
    "30/06/2009",
    "12/12/2011",
    "21/03/2014",
    "30/06/2009",
    "30/06/1998",
    "01/07/2012",
    "08/11/2012",
    "30/06/2011",
    "30/06/1991",
    "30/06/1999",
    "30/06/1996",
    "30/06/1997",
    "31/10/2017",
    "30/06/2010",
    "30/06/2005",
    "30/06/2003",
    "30/06/2005",
    "30/06/1998",
    "30/12/2009",
    "30/06/2003",
    "30/06/2009",
    "30/06/2007",
    "22/12/2020",
    "30/06/2001",
    "30/06/2008",
    "30/07/2002",
    "30/06/2000",
    "30/06/1989",
    "30/06/2003",
    "30/06/1995",
    "30/06/2008",
    "30/06/1991",
    "30/06/2005",
    "30/06/2005",
    "30/06/1992",
    "04/12/2018",
    "29/12/2021",
    "30/06/1990",
    "30/06/2007",
    "27/12/2019",
    "30/06/1998",
    "30/06/2002",
    "30/06/2007",
    "20/02/2018",
    "22/03/2017",
    "30/06/2003",
    "30/06/2009",
    "27/12/2021",
    "16/11/2010",
    "04/10/2012",
    "30/06/2009",
    "30/06/2010",
    "13/09/2021",
    "30/06/1999",
    "30/06/1990",
    "30/06/1991",
    "30/06/2002",
    "30/06/2004",
    "12/02/2014",
    "12/10/2018",
    "30/06/2010",
    "30/06/2002",
    "09/12/2010",
    "28/12/2012",
    "17/09/2015",
    "30/06/2010",
    "30/06/1993",
    "19/12/2019",
    "30/06/2005",
    "24/03/2015",
    "30/06/2003",
    "28/02/2017",
    "01/07/2008",
    "10/04/2002",
    "30/06/2012",
    "30/06/1995",
    "17/12/2012",
    "30/06/2012",
    "09/12/2022",
    "18/12/2013",
]


class Command(BaseCommand):
    counter_success = 0
    counter_avenants = 0
    numeros_not_found = []

    def convention_denonciation(self, numero, date):
        date_python = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        user = User.objects.filter(email="sylvain.delabye@beta.gouv.fr").first()
        qs = Convention.objects.filter(numero=numero)
        if qs.count() == 0:
            self.stdout.write(self.style.WARNING(f"Convention {numero} not found."))
            self.numeros_not_found.append(numero)
            return
        elif qs.count() > 1:
            self.stdout.write(
                self.style.WARNING(
                    f"Several conventions found for {numero}. Updating status anyway."
                )
            )

        for convention in qs:
            last_avenant = _get_last_avenant(convention)
            avenant_denonciation = convention.clone(
                user, convention_origin=last_avenant
            )
            avenant_denonciation.date_denonciation = date_python
            avenant_denonciation.numero = (
                avenant_denonciation.get_default_convention_number()
            )
            avenant_denonciation.save()
            convention_denonciation_validate(convention_uuid=avenant_denonciation.uuid)

        self.counter_success += 1
        self.stdout.write(
            f"Updated convention {numero} with statut "
            f"{ConventionStatut.DENONCEE.label} and date_denonciation {date_python}"
        )

    def handle(self, *args, **options):
        assert len(numeros) == len(dates)

        for i in range(len(numeros)):
            self.convention_denonciation(numero=numeros[i], date=dates[i])

        self.stdout.write("===== EXECUTION SUMMARY ====== ")
        self.stdout.write(f"Conventions updated: {self.counter_success}")
        self.stdout.write(f"Conventions not found: {len(self.numeros_not_found)}")
        if len(self.numeros_not_found) > 0:
            self.stdout.write("===== NUMEROS NOT FOUND ====== ")
        for numero in self.numeros_not_found:
            self.stdout.write(numero)