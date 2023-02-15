drop table if exists ecolo.ecolo_departement cascade;

create table ecolo.ecolo_departement
(
    id             bigint            not null
        constraint pk_ecolo_departement
            primary key,
    codeinsee      varchar(3)        not null
        constraint uk_ecolo_departement
            unique,
    codesiren      varchar(9),
    libelle        varchar(40),
    estactif       boolean,
    region_id      bigint            not null
        constraint fk_ecolo_departement_region
            references ecolo.ecolo_region,
    version        integer default 0 not null,
    chronobailleur integer
);
