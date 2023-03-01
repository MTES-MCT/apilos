-- Requête pour alimenter la table programmes_reference_cadastrale

-- Champs restants à mapper:
-- typologie CAVE, TERRASSE, JARDIN              not null
-- surface_hors_surface_retenue numeric(6, 2)            not null
-- loyer_par_metre_carre        numeric(6, 2)            not null
-- loyer                        numeric(6, 2)            not null
-- cree_le                      timestamp with time zone not null
-- mis_a_jour_le                timestamp with time zone not null
-- bailleur_id FK(Bailleur)  not null
-- logement_id FK(ProgrammeLogement) not null

-- Requête pas encore utilisée par un importer, puisque les annexes sont liées au programme sur Ecolo,
-- quand elles sont liées au logement sur APiLos

-- Pas de notion de surface ni de loyer au m2 ... => ABANDONNE

select
    upper(ev.libelle) as typologie,
    montantloyerinitial as loyer
from ecolo.ecolo_annexe ea
    inner join ecolo.ecolo_valeurparamstatic ev on ev.id = ea.typeannexe_id;
