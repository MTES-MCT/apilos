drop table if exists ecolo.ecolo_programmelogement cascade;

create table ecolo.ecolo_programmelogement
(
    id                                      bigint            not null
        constraint pk_ecolo_programmelogement
            primary key,
    description                             varchar(50),
    ordre                                   integer           not null,
    datemiseservice                         date,
    commentaireopah                         varchar(2000),
    dateresiliation                         date,
    datedemandedenonciation                 date,
    geolocalisationx                        double precision,
    geolocalisationy                        double precision,
    surfacehabitable                        real,
    surfacecorrigee                         real,
    surfaceutile                            real,
    surfaceannexe                           real,
    logementsnombretotal                    integer,
    logementsnombreindtotal                 integer,
    logementsnombrecoltotal                 integer,
    logementsnombrelitstotal                integer,
    logementsnombrechambrestotal            integer,
    logementsnombreoccupes                  integer,
    logementsnombresupplafond               integer,
    logementsnombreinfplafond               integer,
    coeffponderationmoyen                   double precision,
    reservationprefpourcentage              real,
    reservationprefnombre                   integer,
    quotafonctionnairespourcentage          real,
    quotafonctionnairenombre                integer,
    estderogationloyer                      boolean,
    estderogationressources                 boolean,
    dateinitialeloyersredevances            date,
    dateactualisationloyersredevances       date,
    financementdate                         date,
    financementmontant                      real,
    financementdureepret                    integer,
    financementdescription                  varchar(50),
    financementreferencedossier             varchar(20),
    financementestgalion                    boolean,
    montantplafondloyerindinitial           double precision,
    montantplafondloyerindactualise         double precision,
    montantplafondredevancelitinitial       double precision,
    montantplafondredevancelitactualise     double precision,
    montantplafondredevancechambreinitial   double precision,
    montantplafondredevancechambreactualise double precision,
    conventiondonneesgenerales_id           bigint            not null
        constraint fk_ecolo_programmelogement_conventiondonneesgenerales
            references ecolo.ecolo_conventiondonneesgenerales,
    typefinancement_id                      bigint            not null
        constraint fk_ecolo_programmelogement_typefinancement
            references ecolo.ecolo_typefinancement,
    natureoperation_id                      bigint
        constraint fk_ecolo_programmelogement_natureoperation
            references ecolo.ecolo_valeurparamstatic,
    commune_id                              bigint            not null
        constraint fk_ecolo_programmelogement_commune
            references ecolo.ecolo_commune,
    typesurface_id                          bigint
        constraint fk_ecolo_programmelogement_typesurface
            references ecolo.ecolo_valeurparamstatic,
    bailleurgestionnaire_id                 bigint
        constraint fk_ecolo_programmelogement_bailleurgestionnaire
            references ecolo.ecolo_bailleur,
    bailleurproprietaire_id                 bigint            not null
        constraint fk_ecolo_programmelogement_bailleurproprietaire
            references ecolo.ecolo_bailleur,
    etatprogramme_id                        bigint            not null
        constraint fk_ecolo_programmelogement_etatprogramme
            references ecolo.ecolo_valeurparamstatic,
    typechauffage_id                        bigint
        constraint fk_ecolo_programmelogement_typechauffage
            references ecolo.ecolo_valeurparamstatic,
    niveauservice_id                        bigint
        constraint fk_ecolo_programmelogement_niveauservice
            references ecolo.ecolo_valeurparamstatic,
    typelabel_id                            bigint
        constraint fk_ecolo_programmelogement_typelabel
            references ecolo.ecolo_valeurparamstatic,
    version                                 integer default 0 not null,
    reservationprefduree                    integer,
    quotafonctionnaireduree                 integer,
    datemisechantier                        date,
    datelivraisonlogements                  date,
    montantplafondloyercolinitial           double precision,
    montantplafondloyercolactualise         double precision,
    surfaceutileind                         real,
    surfacecorrigeeind                      real,
    surfaceutilecol                         real,
    surfacecorrigeecol                      real,
    constraint uk_ecolo_programmelogement
        unique (ordre, conventiondonneesgenerales_id)
);