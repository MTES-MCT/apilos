drop table if exists ecolo.ecolo_contactbailleur;

create table ecolo.ecolo_contactbailleur
(
    id            bigint            not null
        constraint pk_ecolo_contactbailleur
            primary key,
    nom           varchar(100),
    prenom        varchar(50),
    tel           varchar(15),
    fax           varchar(15),
    mail          varchar(200),
    datemodif     date,
    entitegest_id bigint
        constraint fk_ecolo_contactbailleur_entitegest
            references ecolo.ecolo_entitegest,
    bailleur_id   bigint            not null
        constraint fk_ecolo_contactbailleur_bailleur
            references ecolo.ecolo_bailleur,
    civilite_id   bigint
        constraint fk_ecolo_contactbailleur_civilite
            references ecolo.ecolo_valeurparamstatic,
    version       integer default 0 not null
);
