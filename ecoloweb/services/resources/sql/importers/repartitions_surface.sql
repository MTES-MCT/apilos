select
    pl.id||':'||rl.typologie||':'||rl.type_habitat as id,
    ch.id as lot_id,
    rl.typologie,
    rl.type_habitat,
    rl.quantite
from ecolo.ecolo_programmelogement pl
    inner join ecolo.ecolo_conventionhistorique ch on pl.conventiondonneesgenerales_id = ch.conventiondonneesgenerales_id and ch.programme_ids[1] = pl.id
    inner join (
        select
            il.programmelogement_id,
            case
                when ptl.code in ('ST1', 'T1') then 'T1'
                when ptl.code in ('T1B', 'T1P') then 'T1bis'
                else ptl.code -- T2+ are exactly the same
            end as typologie,
            'INDIVIDUEL' as type_habitat,
            il.nblogtind as quantite
        from ecolo.ecolo_infostypelogement il
            inner join ecolo.ecolo_valeurparamstatic ptl on il.typelogement_id = ptl.id
        where
            il.nblogtind is not null
            and il.nblogtind > 0
        union all
        select
            il.programmelogement_id,
            case
                when ptl.code in ('ST1', 'T1') then 'T1'
                when ptl.code in ('T1B', 'T1P') then 'T1bis'
                else ptl.code -- T2+ are exactly the same
            end as typologie,
            'COLLECTIF' as type_habitat,
            il.nblogtcol as quantite
        from ecolo.ecolo_infostypelogement il
            inner join ecolo.ecolo_valeurparamstatic ptl on il.typelogement_id = ptl.id
        where
            il.nblogtcol is not null
            and il.nblogtcol > 0
    ) rl on rl.programmelogement_id = pl.id
where
    ch.id = %s