select
    pj.id,
    cdg.id||':'||ff.code as convention_id,
    case
        when vps.code = '1' then 'CONVENTION'
        when vps.code = '2' then 'RECTIFICATION'
        when vps.code = '3' then 'ATTESTATION_PREFECTORALE'
        when vps.code = '4' then 'AVENANT'
        when vps.code = '5' then 'PHOTO'
        else 'AUTRE'
    end as type,
    pj.entitegest_id||'/'||pj.conventionapl_id||'/'||pj.id||'.'||(regexp_matches(pj.fichier,'\.(\w+)$'))[1] as fichier,
    pj.fichier as nom_reel,
    pj.description,
    pj.date::timestamp at time zone 'Europe/Paris' as cree_le
from ecolo.ecolo_piecejointe pj
    inner join ecolo.ecolo_conventionapl c on pj.conventionapl_id = c.id
    inner join ecolo_valeurparamstatic vps on pj.typepiecejointe_id = vps.id and vps.subtype = 'TPJ'
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on c.id = cdg.conventionapl_id
    inner join ecolo.ecolo_programmelogement pl on cdg.id = pl.conventiondonneesgenerales_id
    inner join ecolo.ecolo_typefinancement tf on pl.typefinancement_id = tf.id
    inner join ecolo.ecolo_famillefinancement ff on tf.famillefinancement_id = ff.id
where
    cdg.id = %s
    and ff.code = %s