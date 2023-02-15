drop table if exists ecolo.ecolo_commune cascade;

create table ecolo.ecolo_commune
(
    id             bigint            not null
        constraint pk_ecolo_commune
            primary key,
    code           varchar(5)        not null
        constraint uk_ecolo_commune
            unique,
    codesiren      varchar(9),
    libelle        varchar(50),
    estactive      boolean,
    departement_id bigint            not null
        constraint fk_ecolo_commune_departement
            references ecolo.ecolo_departement,
    version        integer default 0 not null
);
