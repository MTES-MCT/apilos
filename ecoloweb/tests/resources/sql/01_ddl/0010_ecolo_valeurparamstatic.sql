drop table if exists ecolo.ecolo_valeurparamstatic cascade;

create table ecolo.ecolo_valeurparamstatic
(
    id                      bigint            not null
        constraint pk_ecolo_valeurparamstatic
            primary key,
    subtype                 varchar(3)        not null,
    estgeneresysteme        boolean,
    estdelegable            boolean,
    dureerenouvellement     integer,
    estactualisablemontants boolean,
    estconventionmodifiable boolean,
    code                    varchar(12)       not null,
    ordre                   integer,
    libelle                 varchar(250),
    debutvalidite           date,
    finvalidite             date,
    version                 integer default 0 not null,
    estliebailleur          boolean default false,
    constraint uk_ecolo_valeurparamstatic
        unique (code, subtype)
);