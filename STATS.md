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

