#!/usr/bin/env python3
"""Script pour insérer un utilisateur de test avec mot de passe hashé"""

import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_CONFIG = {
    "host": "127.0.0.1",
    "database": "monitoring",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

def hash_password(password: str) -> str:
    """Hacher un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def insert_test_user():
    """Insérer l'utilisateur AdminRohySafe avec mot de passe hashé"""
    
    # Hasher le mot de passe
    raw_password = "RohySafe@123456"
    hashed_pwd = hash_password(raw_password)
    
    print(f"Mot de passe original: {raw_password}")
    print(f"Mot de passe hashé: {hashed_pwd}")
    
    # Connexion BD
    conn = psycopg2.connect(
        cursor_factory=RealDictCursor,
        **DATABASE_CONFIG
    )
    cur = conn.cursor()
    
    try:
        # Supprimer l'ancien enregistrement si existe
        cur.execute("DELETE FROM login WHERE username = %s", ("AdminRohySafe",))
        
        # Insérer le nouvel enregistrement avec mot de passe hashé
        cur.execute(
            "INSERT INTO login (id, username, pwd, code, role) VALUES (%s, %s, %s, %s, %s)",
            (1, "AdminRohySafe", hashed_pwd, "123456", "admin")
        )
        
        conn.commit()
        print("\n✓ Utilisateur inséré avec succès!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Erreur: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    insert_test_user()
