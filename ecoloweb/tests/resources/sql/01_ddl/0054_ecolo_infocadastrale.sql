drop table if exists ecolo.ecolo_infocadastrale cascade;

create table ecolo.ecolo_infocadastrale
(
    id                   bigint            not null
        constraint pk_ecolo_infocadastrale
            primary key,
    section              varchar(2)        not null,
    parcelle             varchar(10)       not null,
    superficie           double precision,
    x                    double precision,
    y                    double precision,
    programmelogement_id bigint            not null
        constraint fk_ecolo_infocadastrale_programmelogement
            references ecolo.ecolo_programmelogement,
    version              integer default 0 not null,
    constraint uk_ecolo_infocadastrale
        unique (section, parcelle, programmelogement_id)
);