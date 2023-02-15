drop table if exists ecolo.ecolo_avenant cascade;

create table ecolo.ecolo_avenant
(
    id                            bigint            not null
        constraint pk_ecolo_avenant
            primary key,
    numero                        integer           not null,
    datedepot                     date,
    datesignatureprefet           date,
    dateenregistrement            date,
    datepublication               date,
    dateannulation                date,
    description                   varchar(250),
    referencepublication          varchar(50),
    estreglementaire              boolean,
    estencours                    boolean,
    conventionapl_id              bigint            not null
        constraint fk_ecolo_avenant_conventionapl
            references ecolo.ecolo_conventionapl,
    entitegest_id                 bigint            not null
        constraint fk_ecolo_avenant_entitegest
            references ecolo.ecolo_entitegest,
    /*
    conventiondonneesgenerales_id bigint
        constraint fk_ecolo_avenant_conventiondonneesgenerales
            references ecolo.ecolo_conventiondonneesgenerales,

    bureauenregistrement_id       bigint
        constraint fk_ecolo_avenant_bureauenregistrement
            references ecolo.ecolo_bureauenregistrement,

    conventionprecedente_id       bigint
        constraint fk_ecolo_avenant_conventionprecedente
            references ecolo.ecolo_conventiondonneesgenerales,
    */
    version                       integer default 0 not null,
    nouvelledateexpiration        date,
    constraint uk_ecolo_avenant
        unique (numero, conventionapl_id)
);
