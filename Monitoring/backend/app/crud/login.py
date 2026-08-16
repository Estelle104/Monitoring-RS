# app/crud/login.py
from app.db.db import get_connection
import bcrypt


def hash_password(password: str) -> str:
    """Hacher un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe contre un hash bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_all_logins():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, username, code, role FROM login")
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows


def get_login_by_id(login_id: int):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, username, code, role FROM login WHERE id = %s", (login_id,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return row


def get_login_by_username(username: str):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, username, pwd, code, role FROM login WHERE username = %s", (username,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return row


def create_login(data: dict):
    """Créer un nouveau compte login"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Hacher le mot de passe
    hashed_pwd = hash_password(data["pwd"])
    
    cur.execute(
        "INSERT INTO login(username, pwd, code, role) VALUES (%s, %s, %s, %s)",
        (data["username"], hashed_pwd, data["code"], data["role"])
    )
    
    conn.commit()
    login_id = cur.lastrowid
    cur.close()
    conn.close()
    
    return login_id


def update_login(login_id: int, data: dict):
    """Mettre à jour un login"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Hacher le mot de passe si fourni
    hashed_pwd = hash_password(data.get("pwd")) if "pwd" in data else None
    
    if hashed_pwd:
        cur.execute(
            "UPDATE login SET username = %s, pwd = %s, code = %s, role = %s WHERE id = %s",
            (data.get("username"), hashed_pwd, data.get("code"), data.get("role"), login_id)
        )
    else:
        cur.execute(
            "UPDATE login SET username = %s, code = %s, role = %s WHERE id = %s",
            (data.get("username"), data.get("code"), data.get("role"), login_id)
        )
    
    conn.commit()
    cur.close()
    conn.close()


def delete_login(login_id: int):
    """Supprimer un login"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM login WHERE id = %s", (login_id,))
    
    conn.commit()
    cur.close()
    conn.close()


def check_login(username: str, password: str) -> dict:
    """Vérifier les identifiants de connexion"""
    login = get_login_by_username(username)
    
    if not login:
        return {"status": "error", "message": "Utilisateur non trouvé"}
    
    if not verify_password(password, login['pwd']):
        return {"status": "error", "message": "Mot de passe incorrect"}
    
    return {
        "status": "ok",
        "message": "Connexion réussie",
        "user": {
            "id": login['id'],
            "username": login['username'],
            "code": login['code'],
            "role": login['role']
        }
    }
