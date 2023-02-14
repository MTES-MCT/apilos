drop table if exists ecolo.ecolo_programmeadresse cascade;

create table ecolo.ecolo_programmeadresse
(
    id                   bigint            not null
        constraint pk_ecolo_programmeadresse
            primary key,
    ligne1               varchar(38),
    ligne2               varchar(38),
    ligne3               varchar(38),
    ligne4               varchar(38),
    codepostal           varchar(5),
    ville                varchar(32),
    telephone1           varchar(15),
    telephone2           varchar(15),
    fax                  varchar(15),
    mail                 varchar(200),
    datecreation         bigint  default 0 not null,
    programmelogement_id bigint            not null
        constraint fk_ecolo_programmeadresse_programmelogement
            references ecolo.ecolo_programmelogement,
    version              integer default 0 not null
);