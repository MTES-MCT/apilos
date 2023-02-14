drop table if exists ecolo.ecolo_logement;

create table ecolo.ecolo_logement
(
    id                    bigint            not null
        constraint pk_ecolo_logement
            primary key,
    nblogements           integer,
    numerobatiment        varchar(5),
    noescalier            varchar(5),
    etage                 varchar(5),
    numerologement        varchar(5),
    surfacehabitable      real,
    surfaceannexe         real,
    surfaceutile          real,
    surfacecorrigee       real,
    surfaceterrasses      real,
    coefficientmodulation real,
    montantloyer          real,
    datereservation       date,
    estoccupe             boolean,
    nomproprietaire       varchar(100),
    estacceshandicapes    boolean,
    estentreeindependante boolean,
    programmelogement_id  bigint            not null
        constraint fk_ecolo_logement_programmelogement
            references ecolo.ecolo_programmelogement,
    typelogement_id       bigint            not null
        constraint fk_ecolo_logement_typelogement
            references ecolo.ecolo_valeurparamstatic,
    adresse_id            bigint
        constraint fk_ecolo_logement_adresse
            references ecolo.ecolo_logementadresse,
    /*
    reservataire_id       bigint
        constraint fk_ecolo_logement_reservataire
            references ecolo.ecolo_reservataire,
    */
    typechauffage_id      bigint
        constraint fk_ecolo_logement_typechauffage
            references ecolo.ecolo_valeurparamstatic,
    motifsortie_id        bigint
        constraint fk_ecolo_logement_motifsortie
            references ecolo.ecolo_valeurparamstatic,
    typeconstruction_id   bigint            not null
        constraint fk_ecolo_logement_typeconstruction
            references ecolo.ecolo_valeurparamstatic,
    statutlogement_id     bigint            not null
        constraint fk_ecolo_logement_statutlogement
            references ecolo.ecolo_valeurparamstatic,
    datecreation          bigint  default 0 not null,
    version               integer default 0 not null
);