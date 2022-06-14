from django.db import connection

def my_custom_sql():
    with connection.cursor() as cursor:
        cursor.execute(f"""
        with tmp_conv AS (
            select c.uuid, 
            c.cree_le, 
            MIN(ch_sign.mis_a_jour_le), 
            MIN(ch_sign.mis_a_jour_le) - MIN(ch_inst.mis_a_jour_le) AS delay 
            from conventions_convention as c join conventions_conventionhistory as ch_sign on ch_sign.convention_id = c.id and ch_sign.statut_convention = '{ConventionStatut.A_SIGNER}' join conventions_conventionhistory as ch_inst on ch_inst.convention_id = c.id and ch_inst.statut_convention = '2. Instruction requise' where statut = '4. A signer' group by c.uuid, c.cree_le)
select AVG(delay) from tmp_conv;""")

        row = cursor.fetchone()

    return row
