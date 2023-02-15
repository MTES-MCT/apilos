drop table if exists ecolo.ecolo_conventiontype cascade;

create table ecolo.ecolo_conventiontype
(
    id                 bigint            not null
        constraint pk_ecolo_conventiontype
            primary key,
    libelle            varchar(50)       not null,
    templateconvention varchar(100),
    referencearticle   varchar(50),
    estactif           boolean,
    datedebutvalidite  date,
    datefinvalidite    date,
    /*
    decret_id          bigint            not null
        constraint fk_ecolo_conventiontype_decret
            references ecolo.ecolo_decret,
    */
    naturelogement_id  bigint            not null
        constraint fk_ecolo_conventiontype_naturelogement
            references ecolo.ecolo_naturelogement,
    naturebailleur_id  bigint
        constraint fk_ecolo_conventiontype_naturebailleur
            references ecolo.ecolo_naturebailleur,
    typeconvention_id  bigint            not null
        constraint fk_ecolo_conventiontype_typeconvention
            references ecolo.ecolo_valeurparamstatic,
    version            integer default 0 not null,
    constraint uk_ecolo_conventiontype
        unique (libelle/*, decret_id*/)
);