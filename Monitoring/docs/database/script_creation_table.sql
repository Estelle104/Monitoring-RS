CREATE DATABASE monitoring
WITH 
OWNER = postgres
ENCODING = 'UTF8'
TEMPLATE template0;

CREATE TABLE etudiants (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    etu INT UNIQUE NOT NULL
);

CREATE TABLE macs (
    id SERIAL PRIMARY KEY,
    mac VARCHAR(255) UNIQUE NOT NULL,
    id_etudiant INT,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id)
);

CREATE TABLE type_user (
    id INT PRIMARY KEY,
    type_user VARCHAR(20)
);

INSERT INTO type_user (id, type_user) VALUES 
(1, 'etudiant'),
(2, 'admin');

CREATE TABLE machine (
    id SERIAL PRIMARY KEY ,
    mac VARCHAR(17) UNIQUE NOT NULL,
    etu VARCHAR(100),
    hostname VARCHAR(100), --username donne_ETU00XXXX
    mdp VARCHAR(100), --genere automatiquement par le programme puis sera passe sur l'affichege 
    type_user INT,

    FOREIGN KEY(type_user) REFERENCES type_user(id)
);

INSERT INTO machine (mac,etu,hostname,mdp,type_user) VALUES ('88:9f:fa:22:70:5a','9999','PopOS','9999',1);

-- VLAN
CREATE TABLE vlan (
    id VARCHAR(20) PRIMARY KEY,
    vlan INT NOT NULL UNIQUE,
    ip VARCHAR(15) NOT NULL UNIQUE,
    id_salle VARCHAR(20)
);

-- SALLE
CREATE TABLE salle (
    id VARCHAR(20) PRIMARY KEY,
    salle VARCHAR(100) NOT NULL
);

-- LIAISON SALLE ↔ VLAN
CREATE TABLE salle_vlan (
    id_salle VARCHAR(20),
    id_vlan VARCHAR(20),
    limit_debit INT,
    limit_nb_machine INT,
    limit_bande_passante BIGINT,
    PRIMARY KEY (id_salle, id_vlan)
    -- FOREIGN KEY (id_salle) REFERENCES salle(id),
    -- FOREIGN KEY (id_vlan) REFERENCES vlan(id)
);

CREATE TABLE port (
    id VARCHAR(20) PRIMARY KEY,
    numero_port INT,
    id_vlan VARCHAR(20)
);

INSERT INTO salle (id, salle) VALUES
('salle-001', 'Salle A101'),
('salle-002', 'Salle A102'),
('salle-003', 'Salle B201'),
('salle-004', 'Salle B202');



INSERT INTO salle (id, salle) VALUES
('salle-00', 'Salle A101');


-- Table quota
CREATE TABLE quota (
    id SERIAL PRIMARY KEY,
    id_type_user INTEGER NOT NULL,
    quota_limite BIGINT NOT NULL,

    CONSTRAINT fk_quota_type_user
        FOREIGN KEY (id_type_user)
        REFERENCES type_user(id)
        ON DELETE CASCADE,
    
    CONSTRAINT unique_quota_per_type
        UNIQUE (id_type_user)
);

-- Insérer les quotas par type_user (limite en bytes)
INSERT INTO quota (id_type_user, quota_limite) VALUES 
(1, 1073741824),  -- 1 GB pour étudiants
(2, 10737418240); -- 10 GB pour admins

-- Table debit
CREATE TABLE debit (
    id SERIAL PRIMARY KEY,
    id_vlan VARCHAR(20) NOT NULL,
    pourcentage_debit INTEGER NOT NULL CHECK (pourcentage_debit BETWEEN 0 AND 100),

    CONSTRAINT fk_debit_vlan
        FOREIGN KEY (id_vlan)
        REFERENCES vlan(id)
        ON DELETE CASCADE
);

-- Table quota_machine
CREATE TABLE quota_machine (
    id SERIAL PRIMARY KEY,
    id_machine INTEGER NOT NULL,
    quota_consomme BIGINT DEFAULT 0,
    id_quota INTEGER NOT NULL,

    CONSTRAINT fk_quota_machine_machine
        FOREIGN KEY (id_machine)
        REFERENCES machine(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_quota_machine_quota
        FOREIGN KEY (id_quota)
        REFERENCES quota(id)
        ON DELETE CASCADE
);

-- Table historique de consommation du quota
CREATE TABLE histo_quota (
    id SERIAL PRIMARY KEY,
    etu INT NOT NULL,
    quota_consomme BIGINT NOT NULL DEFAULT 0,
    date_consommation TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Insérer une entrée quota_machine pour la machine de test
INSERT INTO quota_machine (id_machine, id_quota, quota_consomme)
SELECT m.id, q.id, 0
FROM machine m
JOIN quota q ON q.id_type_user = m.type_user;



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