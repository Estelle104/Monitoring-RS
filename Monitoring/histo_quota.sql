-- Table historique de consommation du quota
CREATE TABLE histo_quota (
    id SERIAL PRIMARY KEY,
    etu INT NOT NULL,
    quota_consomme BIGINT NOT NULL DEFAULT 0,
    date_consommation TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
