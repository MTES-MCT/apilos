drop table if exists ecolo.ecolo_bailleur cascade;

create table ecolo.ecolo_bailleur
(
    id                    bigint            not null
        constraint pk_ecolo_bailleur
            primary key,
    codesiren             varchar(9),
    codesiret             varchar(14),
    codepersonne          varchar(10),
    raisonsociale         varchar(50),
    enseigne              varchar(20),
    sigle                 varchar(10),
    codedaei              varchar(5),
    islocal               boolean,
    refbancairebanque     varchar(5),
    refbancaireguichet    varchar(5),
    refbancairecompte     varchar(11),
    refbancaireclerib     varchar(2),
    estactif              boolean,
    datemodif             date,
    datemodifgalion       date,
    estproprietaire       boolean,
    estgestionnaire       boolean,
    sousnaturebailleur_id bigint            not null
        constraint fk_ecolo_bailleur_sousnaturebailleur
            references ecolo.ecolo_sousnaturebailleur,
    adresse_id            bigint
        constraint fk_ecolo_bailleur_adresse
            references ecolo.ecolo_adressebailleur,
    entitegest_id         bigint
        constraint fk_ecolo_bailleur_entitegest
            references ecolo.ecolo_entitegest,
    /*
    groupebailleurs_id    bigint
        constraint fk_ecolo_bailleur_groupebailleurs
            references ecolo.ecolo_groupebailleurs,
    */
    departement_id        bigint            not null
        constraint fk_ecolo_bailleur_departement
            references ecolo.ecolo_departement,
    typeorganisation_id   bigint
        constraint fk_ecolo_bailleur_typeorganisation
            references ecolo.ecolo_valeurparamstatic,
    version               integer default 0 not null,
    constraint uk_ecolo_bailleur
        unique (codesiren, codesiret, codepersonne)
);