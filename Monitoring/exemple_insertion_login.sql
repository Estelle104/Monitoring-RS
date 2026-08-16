-- Exemple SQL pour insérer un utilisateur login

-- IMPORTANT : Le mot de passe doit être hashé avec bcrypt avant insertion
-- Les exemples ci-dessous utilisent des hashes bcrypt valides

-- Exemple 1 : Utilisateur admin (mot de passe: admin123)
-- Hash bcrypt de "admin123" :
INSERT INTO login (username, pwd, code, role) VALUES (
  'admin',
  '$2b$12$abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz',
  'ADMIN001',
  'admin'
);

-- Exemple 2 : Utilisateur standard (mot de passe: user123)
INSERT INTO login (username, pwd, code, role) VALUES (
  'john_user',
  '$2b$12$abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz',
  'USER001',
  'user'
);

-- NOTE : Pour créer un vrai hash, utilisez le CRUD Python avec la route /api/logins/create
-- ou utilisez bcrypt en Python :
-- from app.crud.login import hash_password
-- hash = hash_password('monmotdepasse')
-- Puis insérez avec le hash généré.


INSERT INTO etudiants (nom, etu ) VALUES
( 'SOMBINIAINARIVONY Miranto Taarriq NoorAllah', 4303);


INSERT INTO etudiants (nom, etu) VALUES
( 'RASOLOFOARIMANGA Njara Fabien', 4347);