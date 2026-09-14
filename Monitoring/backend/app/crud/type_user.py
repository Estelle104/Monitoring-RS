from app.db.db import get_connection

def get_type_user_by_id(type_user_id: str):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM type_user WHERE id = %s", (type_user_id,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return row


def get_all_type_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM type_user ORDER BY type_user")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_type_users_sans_quota():
    """Retourne les type_user qui n'ont pas encore de quota associé."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT tu.*
        FROM type_user tu
        LEFT JOIN quota q ON q.id_type_user = tu.id
        WHERE q.id IS NULL
        ORDER BY tu.type_user
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
