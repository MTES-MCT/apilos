drop table if exists ecolo.ecolo_categoriefinancement cascade ;

create table ecolo.ecolo_categoriefinancement
(
    id            bigint            not null
        constraint pk_ecolo_categoriefinancement
            primary key,
    code          varchar(12)       not null
        constraint uk_ecolo_categoriefinancement
            unique,
    ordre         integer,
    libelle       varchar(250),
    debutvalidite date,
    finvalidite   date,
    version       integer default 0 not null
);
