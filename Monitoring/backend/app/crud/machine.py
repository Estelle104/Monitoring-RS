from app.db.db import get_connection


def get_machine_by_mac(mac: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM machine WHERE mac = %s",
        (mac.lower(),)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row


def create_machine(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO machine(mac, hostname)
        VALUES (%s, %s)
        """,
        (data["mac"].lower(), data.get("hostname"))
    )

    conn.commit()
    cur.close()
    conn.close()


def delete_machine_by_mac(mac: str):
    """Supprime une machine de la base de données par son adresse MAC"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM machine WHERE mac = %s",
        (mac.lower(),)
    )

    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    return deleted > 0


def get_all_machines():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, hostname, etu, mac FROM machine ORDER BY hostname")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_machines_sans_quota_machine():
    """Retourne les machines qui ne sont pas encore dans quota_machine."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.hostname, m.etu, m.mac
        FROM machine m
        LEFT JOIN quota_machine qm ON qm.id_machine = m.id
        WHERE qm.id IS NULL
        ORDER BY m.hostname
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
