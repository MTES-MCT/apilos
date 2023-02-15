drop table if exists ecolo.ecolo_region cascade;

create table ecolo.ecolo_region
(
    id        bigint            not null
        constraint pk_ecolo_region
            primary key,
    codeinsee varchar(2)        not null
        constraint uk_ecolo_region
            unique,
    libelle   varchar(30),
    estactive boolean,
    version   integer default 0 not null
);