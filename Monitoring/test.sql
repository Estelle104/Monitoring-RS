-- Table login avec id auto-incrémenté
CREATE TABLE IF NOT EXISTS login (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    pwd VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Utilisateur de test avec mot de passe hashé en bcrypt
-- Identifiants: AdminRohySafe / RohySafe@123456
INSERT INTO login (username, pwd, code, role) VALUES (
    'AdminRohySafe', 
    '$2b$12$3lYr1fNfSGSQU6miRjZQW.wE.y64uuyjhvMmFVhKOSVI58tARE9G2',
    '123456', 
    'admin'
);   

