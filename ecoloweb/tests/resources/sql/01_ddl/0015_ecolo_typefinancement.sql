drop table if exists ecolo.ecolo_typefinancement cascade;

create table ecolo.ecolo_typefinancement
(
    id                      bigint            not null
        constraint pk_ecolo_typefinancement
            primary key,
    code                    varchar(12)       not null
        constraint uk_ecolo_typefinancement
            unique,
    ordre                   integer,
    libelle                 varchar(250),
    debutvalidite           date,
    finvalidite             date,
    categoriefinancement_id bigint            not null
        constraint fk_ecolo_typefinancement_categoriefinancement
            references ecolo.ecolo_categoriefinancement,
    famillefinancement_id   bigint            not null
        constraint fk_ecolo_typefinancement_famillefinancement
            references ecolo.ecolo_famillefinancement,
    version                 integer default 0 not null
);