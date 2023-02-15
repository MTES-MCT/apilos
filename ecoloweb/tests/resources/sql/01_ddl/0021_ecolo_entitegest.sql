drop table if exists ecolo.ecolo_entitegest cascade;

create table ecolo.ecolo_entitegest
(
    id                bigint                                     not null
        constraint pk_ecolo_entitegest
            primary key,
    code              varchar(15)                                not null
        constraint uk_ecolo_entitegest
            unique,
    nom               varchar(38),
    isetat            boolean,
    autorite          varchar(100),
    isactive          boolean,
    typeedition       varchar(5) default 'OO'::character varying not null,
    adresse_id        bigint                                     not null
        constraint fk_ecolo_entitegest_adresse
            references ecolo.ecolo_entitegestadresse,
    typeentitegest_id bigint                                     not null
        constraint fk_ecolo_entitegest_typeentitegest
            references ecolo.ecolo_valeurparamstatic,
    version           integer    default 0                       not null,
    nomcourt          varchar(255)
);