select
    distinct on (eg.code)
    eg.id,
    eg.nom||' ('||eg.code||')' as nom, -- Workaround to avoid conflicts on duplicate names
    eg.code,
    ega.ville as ville_signature,
    ega.ligne1||' '||ega.ligne2||' '||ega.ligne3||' '||ega.ligne4 as adresse,
    ega.codepostal as code_postal,
    ega.ville as ville
from ecolo.ecolo_entitegest eg
    left join ecolo.ecolo_entitegestadresse ega on eg.adresse_id = ega.id
where
    eg.id = %s
