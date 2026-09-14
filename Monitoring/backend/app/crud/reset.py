from datetime import datetime
import psycopg2

# Fonction pour réinitialiser le quota de TOUTES les machines
def reset_quota_all_machines(db_connection):
    """
    Réinitialise le quota consommé de toutes les machines à 0
    
    Args:
        db_connection: Connexion à la base de données
        
    Returns:
        dict: Résultat de l'opération
    """
    try:

        rows_history = enregistrer_histo_quota(db_connection)

        with db_connection.cursor() as cursor:
            # Mettre à jour quota_consomme à 0 pour toutes les machines
            cursor.execute(
                """
                UPDATE quota_machine
                SET quota_consomme = 0
                """
            )
            
            db_connection.commit()
            machines_updated = cursor.rowcount
            
            return {
                "success": True,
                "message": f"Quota réinitialisé pour {machines_updated} machines",
                "machines_updated": machines_updated,
                "timestamp": datetime.now().isoformat()
            }
                
    except psycopg2.Error as e:
        db_connection.rollback()
        return {
            "success": False,
            "message": f"Erreur base de données: {str(e)}"
        }


# def enregistrer_histo_quota(conn):
#     """
#     Récupère la consommation des quotas depuis quota_machine
#     et l'enregistre dans histo_quota.
#     """

#     try:
#         with conn.cursor() as cursor:

#             query = """
#                 INSERT INTO histo_quota (
#                     etu,
#                     quota_consomme,
#                     date_consommation
#                 )
#                 SELECT
#                     m.etu::INT,
#                     qm.quota_consomme,
#                     CURRENT_TIMESTAMP
#                 FROM quota_machine qm
#                 JOIN machine m
#                     ON m.id = qm.id_machine;
#             """

#             cursor.execute(query)

#         conn.commit()
#         print("Historique des quotas enregistré avec succès.")

#     except Exception as e:
#         conn.rollback()
#         print(f"Erreur lors de l'enregistrement de l'historique : {e}")



# # Fonction pour update la table quota_machine (TRUNCATE + re-INSERT)
# def update_table_quota(db_connection):
#     """
#     Vide la table quota_machine et la re-remplit à partir des tables machine et quota.
    
#     - TRUNCATE TABLE quota_machine
#     - INSERT INTO quota_machine (id_machine, id_quota, quota_consomme)
#       SELECT m.id, q.id, 0
#       FROM machine m
#       JOIN quota q ON q.id_type_user = m.type_user
    
#     Args:
#         db_connection: Connexion à la base de données
        
#     Returns:
#         dict: Résultat de l'opération
#     """
#     try:
#         with db_connection.cursor() as cursor:
#             # Vider la table quota_machine
#             cursor.execute("TRUNCATE TABLE quota_machine;")
            
#             # Re-remplir à partir de machine JOIN quota
#             cursor.execute(
#                 """
#                 INSERT INTO quota_machine (id_machine, id_quota, quota_consomme)
#                 SELECT m.id, q.id, 0
#                 FROM machine m
#                 JOIN quota q ON q.id_type_user = m.type_user;
#                 """
#             )
            
#             db_connection.commit()
#             rows_inserted = cursor.rowcount
            
#             return {
#                 "success": True,
#                 "message": f"Table quota_machine mise à jour avec {rows_inserted} entrées",
#                 "rows_inserted": rows_inserted,
#                 "timestamp": datetime.now().isoformat()
#             }
                
#     except psycopg2.Error as e:
#         db_connection.rollback()
#         return {
#             "success": False,
#             "message": f"Erreur base de données: {str(e)}"
#         }




def enregistrer_histo_quota(db_connection):
    """
    Enregistre dans histo_quota la consommation actuelle
    de chaque machine présente dans quota_machine.
    """
    try:
        with db_connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO histo_quota (
                    etu,
                    quota_consomme,
                    date_consommation
                )
                SELECT
                    m.etu::INT,
                    qm.quota_consomme,
                    CURRENT_TIMESTAMP
                FROM quota_machine qm
                JOIN machine m
                    ON m.id = qm.id_machine;
                """
            )

            rows_inserted = cursor.rowcount

        return rows_inserted

    except psycopg2.Error:
        raise


# Fonction pour update la table quota_machine (TRUNCATE + re-INSERT)
def update_table_quota(db_connection):
    """
    1. Enregistre l'état actuel de quota_machine dans histo_quota
    2. Vide la table quota_machine
    3. La re-remplit à partir des tables machine et quota

    Args:
        db_connection: Connexion à la base de données

    Returns:
        dict: Résultat de l'opération
    """
    try:
        # 1. ENREGISTRER L'HISTORIQUE AVANT LE TRUNCATE
        rows_history = enregistrer_histo_quota(db_connection)

        with db_connection.cursor() as cursor:

            # 2. Vider la table quota_machine
            cursor.execute("TRUNCATE TABLE quota_machine;")

            # 3. Re-remplir quota_machine
            cursor.execute(
                """
                INSERT INTO quota_machine (
                    id_machine,
                    id_quota,
                    quota_consomme
                )
                SELECT
                    m.id,
                    q.id,
                    0
                FROM machine m
                JOIN quota q
                    ON q.id_type_user = m.type_user;
                """
            )

            rows_inserted = cursor.rowcount

        # Valider toutes les opérations
        db_connection.commit()

        return {
            "success": True,
            "message": (
                f"Historique enregistré : {rows_history} entrées. "
                f"Table quota_machine mise à jour avec "
                f"{rows_inserted} entrées."
            ),
            "history_rows": rows_history,
            "rows_inserted": rows_inserted,
            "timestamp": datetime.now().isoformat()
        }

    except psycopg2.Error as e:
        db_connection.rollback()

        return {
            "success": False,
            "message": f"Erreur base de données: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
