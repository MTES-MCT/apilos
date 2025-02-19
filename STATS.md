# delay entre la création et la mise à la signature

with tmp_conv AS (select c.uuid, c.cree_le, MIN(ch.mis_a_jour_le), MIN(ch.mis_a_jour_le) - c.cree_le AS delay from conventions_convention as c join conventions_conventionhistory as ch on ch.convention_id = c.id and statut_convention = '4. A signer' where statut = '4. A signer' group by c.uuid, c.cree_le)
select AVG(delay) from tmp_conv;
           avg
-------------------------
 59 days 12:53:31.643984
(1 row)

## A partir de 2022

with tmp_conv AS (select c.uuid, c.cree_le, MIN(ch.mis_a_jour_le), MIN(ch.mis_a_jour_le) - c.cree_le AS delay from conventions_convention as c join conventions_conventionhistory as ch on ch.convention_id = c.id and statut_convention = '4. A signer' where statut = '4. A signer' and c.cree_le > '2022-01-01' group by c.uuid, c.cree_le)
select AVG(delay) from tmp_conv;

# entre mise à l'instruction et mise à la signature

with tmp_conv AS (select c.uuid, c.cree_le, MIN(ch_sign.mis_a_jour_le), MIN(ch_sign.mis_a_jour_le) - MIN(ch_inst.mis_a_jour_le) AS delay from conventions_convention as c join conventions_conventionhistory as ch_sign on ch_sign.convention_id = c.id and ch_sign.statut_convention = '4. A signer' join conventions_conventionhistory as ch_inst on ch_inst.convention_id = c.id and ch_inst.statut_convention = '2. Instruction requise' where statut = '4. A signer' group by c.uuid, c.cree_le)
select AVG(delay) from tmp_conv;

## A partir de 2022

with tmp_conv AS (select c.uuid, c.cree_le, MIN(ch_sign.mis_a_jour_le), MIN(ch_sign.mis_a_jour_le) - MIN(ch_inst.mis_a_jour_le) AS delay from conventions_convention as c join conventions_conventionhistory as ch_sign on ch_sign.convention_id = c.id and ch_sign.statut_convention = '4. A signer' join conventions_conventionhistory as ch_inst on ch_inst.convention_id = c.id and ch_inst.statut_convention = '2. Instruction requise' where statut = '4. A signer' and c.cree_le > '2022-01-01' group by c.uuid, c.cree_le)
select AVG(delay) from tmp_conv;

# reste en statut brouillon

with tmp_conv AS (select c.uuid, c.cree_le, MIN(ch_inst.mis_a_jour_le), MIN(ch_inst.mis_a_jour_le) - c.cree_le AS delay from conventions_convention as c join conventions_conventionhistory as ch_inst on ch_inst.convention_id = c.id and ch_inst.statut_convention = '2. Instruction requise'  where statut = '4. A signer' group by c.uuid, c.cree_le)
select AVG(delay) from tmp_conv;

## A partir de 2022

with tmp_conv AS (select c.uuid, c.cree_le, MIN(ch_inst.mis_a_jour_le), MIN(ch_inst.mis_a_jour_le) - c.cree_le AS delay from conventions_convention as c join conventions_conventionhistory as ch_inst on ch_inst.convention_id = c.id and ch_inst.statut_convention = '2. Instruction requise'  where statut = '4. A signer' and c.cree_le > '2022-01-01' group by c.uuid, c.cree_le)
select AVG(delay) from tmp_conv;

# nb logements sociaux

# temps moyen des conventions en corrections requises

with tmp_conv AS (
    select
        c.uuid,
        NOW() - MAX(ch_corr.mis_a_jour_le) AS delay,
        c.statut,
        p.code_postal
    from conventions_convention as c
    join conventions_conventionhistory as ch_corr on ch_corr.convention_id = c.id and ch_corr.statut_convention = '3. Corrections requises'
    join programmes_programme as p on c.programme_id = p.id
    where c.statut = '3. Corrections requises' group by c.uuid, c.statut, p.code_postal
)
select AVG(delay) from tmp_conv;

# BAILLEURS qui ne se sont jamais loggué

select u.username, u.first_name, u.last_name, u.email from users_user as u join users_role as r on r.user_id = u.id where r.typologie = 'BAILLEUR' and u.last_login IS NULL;

# Funnel

# admin with at least 1 user

select
  substr(pp.code_postal,1,2) as departement,
  count(distinct(ia.id))
from programmes_programme as pp
join instructeurs_administration as ia on pp.administration_id = ia.id
inner join users_role as ur on ur.administration_id = ia.id
join users_role as url on url.administration_id = ia.id and url.last_login is not null
group by departement

# admin with at least 1 logged user

select
  substr(pp.code_postal,1,2) as departement,
  count(distinct(ia.id)) as administration_with_logger_user
from programmes_programme as pp
join instructeurs_administration as ia on pp.administration_id = ia.id
inner join users_role as ur on ur.administration_id = ia.id
inner join users_user as uu on uu.id = ur.user_id and uu.last_login is null
group by departement

# Funnel de conversion

WITH administration_with_user AS (
  SELECT
    departement,
    administration_id,
    administration_nom
  FROM (
    SELECT
      substr(pp.code_postal,1,2) AS departement,
      ia.id AS administration_id,
      ia.nom AS administration_nom,
      count(pp.id) AS num_progs,
      RANK() OVER (PARTITION BY ia.id ORDER BY count(pp.id) DESC) AS dest_rank
    FROM programmes_programme AS pp
    JOIN instructeurs_administration AS ia ON pp.administration_id = ia.id
    INNER JOIN users_role AS ur ON ur.administration_id = ia.id
    GROUP BY ia.id, departement
  ) AS admin WHERE dest_rank = 1
)

, administration_with_logged_user AS (
     SELECT distinct(administration_id) as administration_id
     FROM users_role
     INNER JOIN users_user on users_user.id = users_role.user_id
     WHERE administration_id is not null and users_user.last_login IS NOT NULL
     GROUP BY administration_id
)

, administration_with_logged_user_and_bailleur_user AS (
  SELECT distinct(programmes_programme.administration_id) as administration_id
  FROM programmes_programme
  INNER JOIN users_role AS administration_users_role ON administration_users_role.administration_id = programmes_programme.administration_id
  INNER JOIN users_role AS bailleur_users_role ON bailleur_users_role.bailleur_id = programmes_programme.bailleur_id
  INNER JOIN users_user AS administration_users_user ON administration_users_user.id = administration_users_role.user_id AND administration_users_user.last_login IS NOT NULL
  INNER JOIN users_user AS bailleur_users_user ON bailleur_users_user.id = bailleur_users_role.user_id
  WHERE programmes_programme.administration_id is not null
  GROUP BY programmes_programme.administration_id
)

, administration_with_logged_user_and_logged_bailleur_user AS (
  SELECT distinct(programmes_programme.administration_id) as administration_id
  FROM programmes_programme
  INNER JOIN users_role AS administration_users_role ON administration_users_role.administration_id = programmes_programme.administration_id
  INNER JOIN users_role AS bailleur_users_role ON bailleur_users_role.bailleur_id = programmes_programme.bailleur_id
  INNER JOIN users_user AS administration_users_user ON administration_users_user.id = administration_users_role.user_id AND administration_users_user.last_login IS NOT NULL
  INNER JOIN users_user AS bailleur_users_user ON bailleur_users_user.id = bailleur_users_role.user_id AND bailleur_users_user.last_login IS NOT NULL
  WHERE programmes_programme.administration_id is not null
  GROUP BY programmes_programme.administration_id
)

, administration_with_user_and_logged_bailleur_user AS (
  SELECT distinct(programmes_programme.administration_id) as administration_id
  FROM programmes_programme
  INNER JOIN users_role AS administration_users_role ON administration_users_role.administration_id = programmes_programme.administration_id
  INNER JOIN users_role AS bailleur_users_role ON bailleur_users_role.bailleur_id = programmes_programme.bailleur_id
  INNER JOIN users_user AS administration_users_user ON administration_users_user.id = administration_users_role.user_id
  INNER JOIN users_user AS bailleur_users_user ON bailleur_users_user.id = bailleur_users_role.user_id AND bailleur_users_user.last_login IS NOT NULL
  WHERE programmes_programme.administration_id is not null
  GROUP BY programmes_programme.administration_id
)

, administration_with_convention AS (
  SELECT distinct(programmes_programme.administration_id) as administration_id
  FROM conventions_convention
  INNER JOIN programmes_programme ON conventions_convention.programme_id = programmes_programme.id
  GROUP BY programmes_programme.administration_id
)

, administration_with_convention_afer_project AS (
  SELECT distinct(programmes_programme.administration_id) as administration_id
  FROM conventions_convention
  INNER JOIN programmes_programme ON conventions_convention.programme_id = programmes_programme.id
  WHERE conventions_convention.statut != '1. Projet'
  GROUP BY programmes_programme.administration_id
)

, administration_with_convention_afer_instruction AS (
  SELECT distinct(programmes_programme.administration_id) as administration_id
  FROM conventions_convention
  INNER JOIN programmes_programme ON conventions_convention.programme_id = programmes_programme.id
  WHERE conventions_convention.statut != '1. Projet'
    AND conventions_convention.statut != '2. Instruction requise'
  GROUP BY programmes_programme.administration_id
)

, administration_with_convention_validate AS (
  SELECT distinct(programmes_programme.administration_id) as administration_id
  FROM conventions_convention
  INNER JOIN programmes_programme ON conventions_convention.programme_id = programmes_programme.id
  WHERE conventions_convention.statut != '1. Projet'
    AND conventions_convention.statut != '2. Instruction requise'
    AND conventions_convention.statut != '3. Corrections requises'
  GROUP BY programmes_programme.administration_id
)

, funnel_by_administration AS (
  SELECT administration_with_user.administration_id AS administration_id,
    administration_with_user.administration_nom AS administration_nom,
    administration_with_user.departement AS departement,
    ( CASE WHEN administration_with_user.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_user,
    ( CASE WHEN administration_with_logged_user.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_logged_user,
    ( CASE WHEN administration_with_logged_user_and_bailleur_user.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_logged_user_and_bailleur_user,
    ( CASE WHEN administration_with_logged_user_and_logged_bailleur_user.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_logged_user_and_logged_bailleur_user,
    ( CASE WHEN administration_with_user_and_logged_bailleur_user.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_user_and_logged_bailleur_user,
    ( CASE WHEN administration_with_convention.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_convention,
    ( CASE WHEN administration_with_convention_afer_project.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_convention_afer_project,
    ( CASE WHEN administration_with_convention_afer_instruction.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_convention_afer_instruction,
    ( CASE WHEN administration_with_convention_validate.administration_id IS NOT NULL THEN 1 ELSE 0 END ) as administration_with_convention_validate
  FROM administration_with_user
  LEFT JOIN administration_with_logged_user ON administration_with_user.administration_id = administration_with_logged_user.administration_id
  LEFT JOIN administration_with_logged_user_and_bailleur_user ON administration_with_user.administration_id = administration_with_logged_user_and_bailleur_user.administration_id
  LEFT JOIN administration_with_logged_user_and_logged_bailleur_user ON administration_with_user.administration_id = administration_with_logged_user_and_logged_bailleur_user.administration_id
  LEFT JOIN administration_with_user_and_logged_bailleur_user ON administration_with_user.administration_id = administration_with_user_and_logged_bailleur_user.administration_id
  LEFT JOIN administration_with_convention ON administration_with_user.administration_id = administration_with_convention.administration_id
  LEFT JOIN administration_with_convention_afer_project ON administration_with_user.administration_id = administration_with_convention_afer_project.administration_id
  LEFT JOIN administration_with_convention_afer_instruction ON administration_with_user.administration_id = administration_with_convention_afer_instruction.administration_id
  LEFT JOIN administration_with_convention_validate ON administration_with_user.administration_id = administration_with_convention_validate.administration_id
)

SELECT
  departement,
  SUM(administration_with_user) AS administration_with_user,
  SUM(administration_with_logged_user) AS administration_with_logged_user,
  SUM(administration_with_logged_user_and_bailleur_user) AS administration_with_logged_user_and_bailleur_user,
  SUM(administration_with_logged_user_and_logged_bailleur_user) AS administration_with_logged_user_and_logged_bailleur_user,
  SUM(administration_with_user_and_logged_bailleur_user) AS administration_with_user_and_logged_bailleur_user,
  SUM(administration_with_convention) AS administration_with_convention,
  SUM(administration_with_convention_afer_project) AS administration_with_convention_afer_project,
  SUM(administration_with_convention_afer_instruction) AS administration_with_convention_afer_instruction,
  SUM(administration_with_convention_validate) AS administration_with_convention_validate
FROM funnel_by_administration
GROUP BY departement
