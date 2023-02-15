drop table if exists ecolo.ecolo_avenant_typeavenant;

create table ecolo.ecolo_avenant_typeavenant
(
    avenant_id     bigint not null
        constraint fk_avenant_typeavenant_avenant
            references ecolo.ecolo_avenant,
    typeavenant_id bigint not null
        constraint fk_avenant_typeavenant_typeavenant
            references ecolo.ecolo_valeurparamstatic,
    constraint pk_avenant_typeavenant
        primary key (avenant_id, typeavenant_id)
);
