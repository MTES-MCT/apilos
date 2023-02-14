drop table if exists ecolo.ecolo_naturelogement cascade;

create table ecolo.ecolo_naturelogement
(
    id                         bigint            not null
        constraint pk_ecolo_naturelogement
            primary key,
    code                       varchar(12)       not null
        constraint uk_ecolo_naturelogement
            unique,
    ordre                      integer,
    libelle                    varchar(250),
    debutvalidite              date,
    finvalidite                date,
    estenregistrable           boolean,
    estbesoingestionnaire      boolean,
    estbesoinindividuel        boolean,
    estbesoincollectif         boolean,
    estbesoinloyers            boolean,
    estbesoinredevances        boolean,
    estbesoinlits              boolean,
    estbesoinchambres          boolean,
    estactualisationloyers     boolean,
    estactualisationredevances boolean,
    estfoyer                   boolean,
    agregationnumreglementaire integer,
    version                    integer default 0 not null
);