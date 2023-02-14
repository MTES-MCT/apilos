drop table if exists ecolo.ecolo_conventionapl cascade;

create table ecolo.ecolo_conventionapl
(
    id                             bigint            not null
        constraint pk_ecolo_conventionapl
            primary key,
    noreglementaire                varchar(50),
    noordre                        varchar(10),
    libelle                        varchar(50),
    description                    varchar(1000),
    datedepot                      date,
    designationinstructeur         varchar(50),
    datesaisie                     date,
    datemodification               date,
    estreprise                     boolean,
    identifiantreprise             varchar(10),
    repertoirepiecesjointesreprise varchar(100),
    memoreprise                    varchar(1000),
    entitecreatrice_id             bigint            not null
        constraint fk_ecolo_conventionapl_entitecreatrice
            references ecolo.ecolo_entitegest,
    entitemodification_id          bigint
        constraint fk_ecolo_conventionapl_entitemodification
            references ecolo.ecolo_entitegest,
    version                        integer default 0 not null,
    nonormalise                    varchar(50)
);