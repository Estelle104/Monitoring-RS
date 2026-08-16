# Système de Login - Documentation

## Fichiers créés

### Backend

1. **Model** : `backend/app/models/login.py`
   - Définit la structure de la table `login`
   - Champs : id, username, pwd (hashé), code, role

2. **CRUD** : `backend/app/crud/login.py`
   - Fonctions pour CRUD complet
   - **Fonctions principales** :
     - `hash_password(pwd)` : Hashe un mot de passe avec bcrypt
     - `verify_password(pwd, hashed)` : Vérifie un mot de passe
     - `get_all_logins()` : Récupère tous les utilisateurs
     - `get_login_by_username(username)` : Récupère par username
     - `create_login(data)` : Crée un nouvel utilisateur (hache le pwd automatiquement)
     - `check_login(username, pwd)` : **Méthode principale de connexion** - Vérifie username + mot de passe

3. **API** : `backend/app/api/login.py`
   - Routes FastAPI pour le login
   - **Endpoints** :
     - `GET /api/logins` - Liste tous les utilisateurs (sans pwd)
     - `GET /api/logins/{id}` - Récupère un utilisateur
     - `POST /api/logins/create` - Crée un utilisateur
     - `PUT /api/logins/{id}` - Met à jour un utilisateur
     - `DELETE /api/logins/{id}` - Supprime un utilisateur
     - `POST /api/logins/check` - **Endpoint de connexion** - Vérifie username + pwd

4. **Main.py** - Modifié pour inclure le router login

5. **Requirements.txt** - Ajout de `bcrypt==4.1.2`

### Frontend

1. **Page de connexion** : `frontend/login.html`
   - Interface de connexion
   - Appelle `POST /api/logins/check`
   - Stocke les infos utilisateur en sessionStorage
   - Redirige vers dashboard après connexion réussie

2. **Gestion des utilisateurs** : `frontend/login/liste.html`
   - Liste tous les utilisateurs
   - Permet de chercher
   - Permet de supprimer un utilisateur

3. **Ajouter un utilisateur** : `frontend/login/addLogin.html`
   - Formulaire pour créer un nouvel utilisateur
   - Validation du mot de passe (confirmation)
   - Sélection du rôle

### Fichiers utilitaires

1. **Script d'insertion de test** : `insert_test_user.py`
   - Crée un utilisateur de test admin/admin123
   - Exécuter avec : `python3 insert_test_user.py`

2. **Exemple SQL** : `exemple_insertion_login.sql`
   - Exemples d'insertion SQL avec hashes bcrypt

## Utilisation

### 1. Installation des dépendances
```bash
pip install bcrypt==4.1.2
```

### 2. Créer une table login si elle n'existe pas
```sql
CREATE TABLE login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    role VARCHAR(20) NOT NULL
);
```

### 3. Insérer un utilisateur de test
```bash
python3 insert_test_user.py
```

Ou via l'interface : `loadPageContent('login/addLogin.html')`

### 4. Se connecter
Accédez à : `loadPageContent('login.html')`
- Username : admin
- Password : admin123

## Hachage du mot de passe

✓ **Actuellement implémenté** avec bcrypt
- Hachage automatique lors de création/modification
- Vérification sécurisée lors de connexion
- Les mots de passe ne sont JAMAIS stockés en clair

## Points de sécurité

✓ Mots de passe hashés avec bcrypt
✓ Vérification en base de données
✓ Pas de stockage en clair
✓ Session storage pour les infos utilisateur

## Méthode check_login

**Fonction principales** : `app.crud.login.check_login(username, password)`

Retval :
```json
{
  "status": "ok|error",
  "message": "...",
  "user": {
    "id": 1,
    "username": "admin",
    "code": "ADMIN001",
    "role": "admin"
  }
}
```
