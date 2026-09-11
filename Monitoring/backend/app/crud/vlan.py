from app.db.db import get_connection
from app.crud.port import get_ports_by_vlan

def _next_vlan_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM vlan ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        num = int(row['id'].split('-')[1]) + 1
    else:
        num = 1
    return f'vlan-{num:03d}'

def get_vlan_by_id(vlan_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM vlan
        WHERE id = %s
    """, (vlan_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row

def get_vlan_port_by_id(salle_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM vlan
        WHERE id_salle = %s
    """, (salle_id,))


    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return []

    port = get_ports_by_vlan(row['id'])

    return [{
        "id": row['id'],
        "vlan": row['vlan'],
        "ip": row['ip'],
        "id_salle": row['id_salle'],
        "port": [p['numero_port'] for p in port]
    }]

def get_salle_vlans_by_salle(salle_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM salle_vlan
        WHERE id_salle = %s
    """, (salle_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def get_vlan_by_idSalle(salle_id: str):
    vlan_id = get_salle_vlans_by_salle(salle_id)
    if vlan_id:
        return get_vlan_by_id(vlan_id[0]['id_vlan'])
    return None

def get_vlan_port_by_idSalle(salle_id: str):
    vlan_id = get_salle_vlans_by_salle(salle_id)
    if vlan_id:
        return get_vlan_port_by_id(vlan_id[0]['id_vlan'])
    return None

def get_all_vlans():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT v.id, v.vlan, v.ip, v.id_salle, s.salle
        FROM vlan v
        LEFT JOIN salle s ON v.id_salle = s.id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def create_vlan(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    vlan_id = _next_vlan_id()

    cur.execute("""
        INSERT INTO vlan (id, vlan, ip, id_salle)
        VALUES (%s, %s, %s, %s)
    """, (
        vlan_id,
        data["vlan"],
        data["ip"],
        data["id_salle"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return vlan_id


def create_salle_vlan_link(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO salle_vlan (id_salle, id_vlan, limit_nb_machine)
        VALUES (%s, %s, %s)
    """, (
        data["id_salle"],
        data["id_vlan"],
        data.get("limit_nb_machine")
    ))

    conn.commit()
    cur.close()
    conn.close()

def update_vlan(vlan_id: str, data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE vlan SET vlan = %s, ip = %s WHERE id = %s",
        (data.get("vlan"), data.get("ip"), vlan_id)
    )

    conn.commit()

    cur.close()
    conn.close()

def delete_vlan(vlan_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM vlan WHERE id = %s",
        (vlan_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

def get_vlans_by_salle(salle_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """SELECT v.* FROM vlan v
           JOIN salle_vlan sv ON v.id = sv.id_vlan
           WHERE sv.id_salle = %s""",
        (salle_id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows
