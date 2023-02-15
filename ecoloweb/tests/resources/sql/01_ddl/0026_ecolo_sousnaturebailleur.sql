drop table if exists ecolo.ecolo_sousnaturebailleur cascade;

create table ecolo.ecolo_sousnaturebailleur
(
    id                bigint            not null
        constraint pk_ecolo_sousnaturebailleur
            primary key,
    code              varchar(12)       not null
        constraint uk_ecolo_sousnaturebailleur
            unique,
    ordre             integer,
    libelle           varchar(250),
    debutvalidite     date,
    finvalidite       date,
    naturebailleur_id bigint            not null
        constraint fk_ecolo_sousnaturebailleur_naturebailleur
            references ecolo.ecolo_naturebailleur,
    version           integer default 0 not null
);