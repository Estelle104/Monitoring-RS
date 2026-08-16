# app/crud/salle.py
from app.db.db import get_connection


def _next_salle_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM salle ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        num = int(row['id'].split('-')[1]) + 1
    else:
        num = 1
    return f'salle-{num:03d}'


def get_all_salles():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM salle")
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows


def get_salle_by_id(salle_id: str):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM salle WHERE id = %s", (salle_id,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return row


def create_salle(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    salle_id = _next_salle_id()
    
    cur.execute(
        "INSERT INTO salle(id, salle) VALUES (%s, %s)",
        (salle_id, data["salle"])
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return salle_id


def update_salle(salle_id: str, data: dict):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE salle SET salle = %s WHERE id = %s",
        (data.get("salle"), salle_id)
    )
    
    conn.commit()
    cur.close()
    conn.close()


def delete_salle(salle_id: str):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM salle WHERE id = %s", (salle_id,))
    
    conn.commit()
    cur.close()
    conn.close()
