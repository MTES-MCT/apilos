drop table if exists ecolo.ecolo_famillefinancement cascade;

create table ecolo.ecolo_famillefinancement
(
    id            bigint            not null
        constraint pk_ecolo_famillefinancement
            primary key,
    code          varchar(12)       not null
        constraint uk_ecolo_famillefinancement
            unique,
    ordre         integer,
    libelle       varchar(250),
    debutvalidite date,
    finvalidite   date,
    version       integer default 0 not null
);