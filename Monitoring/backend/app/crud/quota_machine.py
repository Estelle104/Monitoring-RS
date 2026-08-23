from app.db.db import get_connection


def get_all_quota_machine():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            qm.id,
            m.mac,
            m.etu,
            m.hostname,
            m.mdp,
            tu.type_user AS machine_type_user,
            q.quota_limite,
            q.id_type_user,
            tu_q.type_user AS quota_type_user,
            qm.quota_consomme
        FROM quota_machine qm
        JOIN machine m ON m.id = qm.id_machine
        LEFT JOIN type_user tu ON tu.id = m.type_user
        JOIN quota q ON q.id = qm.id_quota
        LEFT JOIN type_user tu_q ON tu_q.id = q.id_type_user
        ORDER BY qm.quota_consomme DESC
        """
    )
    rows = cur.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "mac": row["mac"],
            "etu": row["etu"],
            "hostname": row["hostname"],
            "mdp": row["mdp"],
            "machine_type_user": row["machine_type_user"] or "Inconnu",
            "quota_limite": row["quota_limite"] if row["quota_limite"] is not None else 0,
            "id_type_user": row["id_type_user"],
            "quota_type_user": row["quota_type_user"] or "Inconnu",
            "quota_consomme": row["quota_consomme"] if row["quota_consomme"] is not None else 0,
        })

    cur.close()
    conn.close()

    return result


def create_quota_machine(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    type = get_type_by_id_machine(data["id_machine"])["type_user"]
    print(type)
    quota = get_quota_by_type(type)["id"]

    cur.execute(
        "INSERT INTO quota_machine (id_machine, id_quota, quota_consomme) VALUES (%s, %s, %s)",
        (data["id_machine"], quota, data["quota_consomme"]),
    )

    conn.commit()
    cur.close()
    conn.close()

    return data["id_machine"]


def get_type_by_id_machine(id_machine: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * from machine where id = %s",
        (id_machine,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return row


def get_quota_by_type(type: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * from quota where id_type_user = %s",
        (type,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return row


def update_quota_machine(quota_machine_id: int, quota_consomme: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE quota_machine SET quota_consomme = %s WHERE id = %s",
        (quota_consomme, quota_machine_id),
    )
    updated = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()
    return updated > 0


def delete_quota_machine(quota_machine_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM quota_machine WHERE id = %s", (quota_machine_id,))
    deleted = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()
    return deleted > 0
