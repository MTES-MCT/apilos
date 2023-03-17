select
    e.id as id,
    ch.id as convention_id,
    case
        -- /!\ Les types évènements "générés systèmes" d'Ecoloweb sont ignorés
        when vps.code = '1' then 'DEPOT_BAILLEUR'
        when vps.code = '2' then 'MODIFICATION'
        when vps.code = '3' then 'ECHANGE'
        when vps.code = '4' then 'ENVOI_PREFET'
        when vps.code = '5' then 'RETOUR_PREFET'
        when vps.code = '6' then 'ENVOI_HYPOTHEQUE'
        when vps.code = '7' then 'RETOUR_HYPOTHEQUE'
        when vps.code = '8' then 'ENVOI_RECTIFICATIF_PREFET'
        when vps.code = '9' then 'RETOUR_RECTIFICATIF_PREFET'
        when vps.code = '10' then 'PUBLICATION_HYPOTHEQUE'
        when vps.code = '11' then 'ENVOI_CAF'
        when vps.code = '12' then 'DEPOT_AVENANT'
        when vps.code = '13' then 'INSTRUCTION_AVENANT'
        when vps.code = '14' then 'CORRECTION_AVENANT'
        when vps.code = '15' then 'ENVOI_AVENANT_PREFET'
        when vps.code = '16' then 'SIGNATURE_AVENANT_PREFET'
        when vps.code = '17' then 'ENVOI_AVENANT_HYPOTHEQUE'
        when vps.code = '18' then 'RETOUR_AVENANT_HYPOTHEQUE'
        when vps.code = '19' then 'ENVOI_RECTIFICATIF_AVENANT_PREFET'
        when vps.code = '20' then 'RETOUR_RECTIFICATIF_AVENANT_PREFET'
        when vps.code = '21' then 'PUBLICATION_AVENANT_HYPOTHEQUE'
        when vps.code = '25' then 'EXPIRATION_CONVENTION'
        when vps.code = '26' then 'ENVOI_FIN_DENONCIATION'
        when vps.code = '36' then 'AUTRE'
    end as type_evenement,
    e.date as survenu_le,
    e.description
from ecolo_evenement e
    inner join ecolo.ecolo_conventionhistorique ch on e.conventionapl_id = ch.conventionapl_id
    inner join ecolo.ecolo_valeurparamstatic vps on e.typeevenement_id = vps.id and vps.estgeneresysteme = false
where
    ch.id = %s