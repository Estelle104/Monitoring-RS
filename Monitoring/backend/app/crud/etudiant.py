from app.db.db import get_connection

# recupere tous l info des etudiants a partir d une liste de mac
def get_etudiant_info_by_macs(macs: list):
    """
    Pour une liste de MACs, récupère l'ETU et le nom de l'étudiant
    en joignant machine.etu (varchar) casté en INT avec etudiants.etu (integer).
    Retourne un dict { mac_lower: { "etu": str, "nom": str } }
    """
    if not macs:
        return {}

    conn = get_connection()
    cur = conn.cursor()

    # Normalise les MACs en lowercase
    macs_lower = [m.lower() for m in macs]

    # On utilise ANY pour passer la liste de MACs
    cur.execute(
        """
        SELECT m.mac, m.etu, e.nom
        FROM machine m
        LEFT JOIN etudiants e ON CAST(m.etu AS INTEGER) = e.etu
        WHERE LOWER(m.mac) = ANY(%s)
        """,
        (macs_lower,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = {}
    for row in rows:
        result[row["mac"].lower()] = {
            "etu": row["etu"],
            "nom": row["nom"]
        }

    return result
