drop table if exists ecolo.ecolo_piecejointe cascade;

create table ecolo.ecolo_piecejointe
(
    id                 bigint            not null
        constraint pk_ecolo_piecejointe
            primary key,
    fichier            varchar(50),
    description        varchar(1000),
    date               date,
    conventionapl_id   bigint            not null
        constraint fk_ecolo_piecejointe_conventionapl
            references ecolo.ecolo_conventionapl,
    typepiecejointe_id bigint            not null
        constraint fk_ecolo_piecejointe_typepiecejointe
            references ecolo.ecolo_valeurparamstatic,
    entitegest_id      bigint            not null
        constraint fk_ecolo_piecejointe_entitegest
            references ecolo.ecolo_entitegest,
    version            integer default 0 not null
);