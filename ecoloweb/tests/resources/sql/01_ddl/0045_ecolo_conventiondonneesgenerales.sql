drop table if exists ecolo.ecolo_conventiondonneesgenerales cascade;

create table ecolo.ecolo_conventiondonneesgenerales
(
    id                        bigint               not null
        constraint pk_ecolo_conventiondonneesgenerales
            primary key,
    datehistoriquedebut       date                 not null,
    datehistoriquefin         date,
    estmodifiable             boolean,
    descriptifhistorique      varchar(250),
    datesignaturebailleur     date,
    datedemandedenonciation   date,
    datesignatureentitegest   date,
    dateenvoiprefet           date,
    datesignatureprefet       date,
    dateresiliationprefet     date,
    dateenvoihypotheque       date,
    dateenrhypotheque         date,
    datepublication           date,
    referencepublication      varchar(50),
    dateenvoicaf              date,
    dateannulation            date,
    datedernierrenouvellement date,
    dateexpiration            date,
    duree                     integer,
    notaire                   varchar(150),
    conventionapl_id          bigint               not null
        constraint fk_ecolo_conventiondonneesgenerales_conventionapl
            references ecolo.ecolo_conventionapl,
    etatconvention_id         bigint               not null
        constraint fk_ecolo_conventiondonneesgenerales_etatconvention
            references ecolo.ecolo_valeurparamstatic,
    conventiontype_id         bigint               not null
        constraint fk_ecolo_conventiondonneesgenerales_conventiontype
            references ecolo.ecolo_conventiontype,
    naturelogement_id         bigint               not null
        constraint fk_ecolo_conventiondonneesgenerales_naturelogement
            references ecolo.ecolo_naturelogement,
    naturebailleur_id         bigint               not null
        constraint fk_ecolo_conventiondonneesgenerales_naturebailleur
            references ecolo.ecolo_naturebailleur,
    /*
    bureaucaf_id              bigint
        constraint fk_ecolo_conventiondonneesgenerales_bureaucaf
            references ecolo.ecolo_bureaucaf,
    bureauenregistrement_id   bigint
        constraint fk_ecolo_conventiondonneesgenerales_bureauenregistrement
            references ecolo.ecolo_bureauenregistrement,
    */
    avenant_id                bigint
        constraint fk_ecolo_conventiondonneesgenerales_avenant
            references ecolo.ecolo_avenant,
    /*
    annee_id                  bigint               not null
        constraint fk_ecolo_conventiondonneesgenerales_annee
            references ecolo.ecolo_valeurparamstatic,
    */
    estcourante               boolean default true not null,
    version                   integer default 0    not null,
    daterefushypotheque       date,
    motifrefushypotheque      varchar(1000),
    dateexpirationinitiale    date,
    /*
    cus_id                    bigint
        constraint fk_conventiondonneesgenerales_cus
            references ecolo.ecolo_cus,
    */
    constraint uk_ecolo_conventiondonneesgenerales
        unique (datehistoriquedebut, conventionapl_id)
);