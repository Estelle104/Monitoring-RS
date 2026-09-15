from app.db.db import get_connection

def get_all_quota():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM quota order by quota_limite DESC")
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows

def create_quota(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO quota(id_type_user, quota_limite) VALUES (%s, %s)",
        (data["id_type_user"], data["quota_limite"])
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return data["id_type_user"]

def update_quota(quota_id: int, quota_limite: int):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE quota SET quota_limite = %s WHERE id = %s",
        (quota_limite, quota_id)
    )
    updated = cur.rowcount
    
    conn.commit()
    cur.close()
    conn.close()
    return updated > 0

# supprime aussi les quota_machine correspondant
def delete_quota(quota_id: int):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM quota WHERE id = %s", (quota_id,))
    deleted = cur.rowcount
    
    conn.commit()
    cur.close()
    conn.close()
    return deleted > 0


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
