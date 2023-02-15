drop table if exists ecolo.ecolo_naturebailleur cascade;

create table ecolo.ecolo_naturebailleur
(
    id               bigint            not null
        constraint pk_ecolo_naturebailleur
            primary key,
    code             varchar(12)       not null
        constraint uk_ecolo_naturebailleur
            unique,
    ordre            integer,
    libelle          varchar(250),
    debutvalidite    date,
    finvalidite      date,
    estenregistrable boolean,
    dureeconvention  integer,
    version          integer default 0 not null
);