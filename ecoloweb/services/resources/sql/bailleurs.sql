-- Requête pour alimenter la table conventions_convention

-- signataire_nom               varchar(255),
-- signataire_fonction          varchar(255),
-- signataire_date_deliberation date,
-- operation_exceptionnelle     text,
-- capital_social               double precision,
-- type_bailleur                varchar(25)              not null,


select
    b.id,
    b.raisonsociale as nom,
    b.codesiret as siret,
    b.datemodif as cree_le,
    b.datemodif as mis_a_jour_le,
    ab.ligne1||' '||ab.ligne2||' '||ab.ligne3||' '||ab.ligne4 as adresse,
    ab.codepostal as code_postal,
    ab.ville as ville,
    b.codesiren as siren
from ecolo.ecolo_bailleur b
    inner join ecolo.ecolo_adressebailleur ab on b.adresse_id = ab.id
    inner join ecolo.ecolo_departement ed on b.departement_id = ed.id
-- TODO se connecter à l'API d'Annuaire Entreprise pour résoudre les SIRET par leur SIREN
-- 🔗 https://annuaire-entreprises.data.gouv.fr/entreprise/343586541?redirected=1
where codesiret is not null -- Certains bailleurs n'ont pas de code SIRET entier dans la base Ecolo
{% if max_row %}
order by random()
limit {{ max_row }}
{% endif %}