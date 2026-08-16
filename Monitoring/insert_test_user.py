#!/usr/bin/env python3
"""
Script pour insérer un utilisateur de test avec mot de passe hashé
Exécuter depuis la racine du projet : python3 insert_test_user.py
"""

import sys
sys.path.insert(0, 'backend')

from app.crud.login import create_login, hash_password

# Créer un utilisateur de test
user_data = {
    "username": "admin",
    "pwd": "admin123",  # Sera hashé automatiquement par create_login
    "code": "ADMIN001",
    "role": "admin"
}

try:
    user_id = create_login(user_data)
    print(f"✓ Utilisateur créé avec succès !")
    print(f"  ID: {user_id}")
    print(f"  Username: {user_data['username']}")
    print(f"  Rôle: {user_data['role']}")
    print(f"  Code: {user_data['code']}")
    print(f"\nVous pouvez maintenant vous connecter avec:")
    print(f"  Username: {user_data['username']}")
    print(f"  Password: {user_data['pwd']}")
except Exception as e:
    print(f"✗ Erreur lors de la création du utilisateur: {e}")
    sys.exit(1)
