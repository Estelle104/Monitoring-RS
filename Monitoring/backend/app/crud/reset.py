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


# Fonction pour update la table quota_machine (TRUNCATE + re-INSERT)
def update_table_quota(db_connection):
    """
    Vide la table quota_machine et la re-remplit à partir des tables machine et quota.
    
    - TRUNCATE TABLE quota_machine
    - INSERT INTO quota_machine (id_machine, id_quota, quota_consomme)
      SELECT m.id, q.id, 0
      FROM machine m
      JOIN quota q ON q.id_type_user = m.type_user
    
    Args:
        db_connection: Connexion à la base de données
        
    Returns:
        dict: Résultat de l'opération
    """
    try:
        with db_connection.cursor() as cursor:
            # Vider la table quota_machine
            cursor.execute("TRUNCATE TABLE quota_machine;")
            
            # Re-remplir à partir de machine JOIN quota
            cursor.execute(
                """
                INSERT INTO quota_machine (id_machine, id_quota, quota_consomme)
                SELECT m.id, q.id, 0
                FROM machine m
                JOIN quota q ON q.id_type_user = m.type_user;
                """
            )
            
            db_connection.commit()
            rows_inserted = cursor.rowcount
            
            return {
                "success": True,
                "message": f"Table quota_machine mise à jour avec {rows_inserted} entrées",
                "rows_inserted": rows_inserted,
                "timestamp": datetime.now().isoformat()
            }
                
    except psycopg2.Error as e:
        db_connection.rollback()
        return {
            "success": False,
            "message": f"Erreur base de données: {str(e)}"
        }