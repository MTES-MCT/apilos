drop table if exists ecolo.ecolo_annexe;
create table ecolo.ecolo_annexe
(
    id                    bigint            not null
        constraint pk_ecolo_annexe
            primary key,
    nombre                integer,
    prixunitaire          real,
    montantloyerinitial   real,
    montantloyeractualise real,
    typeannexe_id         bigint            not null
        constraint fk_ecolo_annexe_typeannexe
            references ecolo.ecolo_valeurparamstatic,
    programmelogement_id  bigint            not null
        constraint fk_ecolo_annexe_programmelogement
            references ecolo.ecolo_programmelogement,
    datecreation          bigint  default 0 not null,
    version               integer default 0 not null
);