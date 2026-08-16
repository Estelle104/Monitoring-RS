
# ROHYSAFE-MONITORING

## 📌 Description
Partie monitoring du projet RohySafe.

Ce programme permet :
- la surveillance des logs système et réseau
- la gestion et la création de VLAN

---

## ⚙️ Installation

### Prérequis
- Python 3.12.3
- PostgreSQL
- XAMPP (si nécessaire pour d'autres modules)

### Étapes

1. Installer les dépendances :
```bash
Lancer le script install_dependences.sh
````

2. Créer la base de données :

```bash
createdb -U postgres monitoring
```

3. Importer les tables et données :

```bash
psql -U postgres -d monitoring -f newTable.sql
```

4. Installer et lancer XAMPP (puis copier le dossier dans HTDOCS)

---

## ▶️ Lancement

```bash
python3 run_api.py
```

---

## ℹ️ À propos

ROHYSAFE-MONITORING est une solution de monitoring et de contrôle réseau conçue pour administrer des infrastructures par salles et par VLAN.

La plateforme permet de :

* créer et gérer les VLAN
* superviser les équipements connectés
* scanner le réseau
* appliquer des règles de sécurité (autoriser, bloquer ou expulser des appareils)
* automatiser certaines configurations réseau (DHCP, switch, limitation de bande passante)

Son objectif est d’offrir une vue centralisée, en temps réel, de l’état du réseau afin d’améliorer la sécurité, la stabilité et la gestion opérationnelle.
