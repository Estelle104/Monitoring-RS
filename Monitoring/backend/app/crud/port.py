# app/crud/port.py
from app.db.db import get_connection


def _next_port_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM port ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        num = int(row['id'].split('-')[1]) + 1
    else:
        num = 1
    return f'port-{num:03d}'


def get_all_ports():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM port")
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows


def get_port_by_id(port_id: str):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM port WHERE id = %s", (port_id,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return row


def get_ports_by_vlan(vlan_id: str):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM port WHERE id_vlan = %s", (vlan_id,))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows


def create_port(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    port_id = _next_port_id()
    
    cur.execute(
        "INSERT INTO port(id, numero_port, id_vlan) VALUES (%s, %s, %s)",
        (port_id, data["numero_port"], data.get("id_vlan"))
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return port_id


def update_port(port_id: str, data: dict):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE port SET numero_port = %s, id_vlan = %s WHERE id = %s",
        (data.get("numero_port"), data.get("id_vlan"), port_id)
    )
    
    conn.commit()
    cur.close()
    conn.close()


def delete_port(port_id: str):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM port WHERE id = %s", (port_id,))
    
    conn.commit()
    cur.close()
    conn.close()
