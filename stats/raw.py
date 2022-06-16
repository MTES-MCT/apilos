from django.db import connection
from conventions.models import ConventionStatut


def average_delay_sql():
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
        with tmp_conv AS (
            select c.uuid,
            c.cree_le,
            MIN(ch_sign.mis_a_jour_le),
            MIN(ch_sign.mis_a_jour_le) - MIN(ch_inst.mis_a_jour_le) AS delay
            from conventions_convention as c join conventions_conventionhistory as ch_sign
            on ch_sign.convention_id = c.id
            and ch_sign.statut_convention = '{ConventionStatut.A_SIGNER}'
            join conventions_conventionhistory as ch_inst
            on ch_inst.convention_id = c.id
            and ch_inst.statut_convention = '{ConventionStatut.INSTRUCTION}'
            where statut = '{ConventionStatut.A_SIGNER}' group by c.uuid, c.cree_le)
    select AVG(delay) from tmp_conv;"""
        )
        delay = cursor.fetchone()
        if delay[0] is not None:
            result = round((delay[0].total_seconds()) / 86400)
        else:
            result = "n/a"

        return result
