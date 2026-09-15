from datetime import date, datetime, timedelta

from app.db.db import get_connection

# 2Go en bytes
GB_2_BYTES = 2 * 1024 * 1024 * 1024


# construit dynamiquement la partie WHERE du requete SQL
def _build_filters(etu=None, date_from=None, date_to=None):
    conditions = []
    params = []

    if etu is not None:
        conditions.append("etu = %s")
        params.append(etu)

    if date_from is not None:
        conditions.append("date_consommation::date >= %s")
        params.append(date_from)

    if date_to is not None:
        conditions.append("date_consommation::date <= %s")
        params.append(date_to)

    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    # where_clause: condition dynamique - params: parametres du requete
    return where_clause, params


# récupérer l'historique des consommations avec filtre dynamique
def get_histo_quota_list(
    etu=None,
    date_from=None,
    date_to=None,
    consumption_op=None,
    consumption_value_go=None,
    page=1,
    per_page=20,
):
    """
    Récupère la consommation historique.

    - Sans filtre etu: renvoie les lignes brutes.
    - Avec filtre etu: renvoie la consommation totale par étudiant.
    - Avec filtre de date(s): limite la période concernée.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # COnstruit le filtre dynamiquement (requete dynamique)
        where_clause, params = _build_filters(etu=etu, date_from=date_from, date_to=date_to)
        # Limite de consommation initialisée
        threshold_bytes = None

        # consumption_op: > ou < - consumption_value_go: valeur de consommation en go
        if consumption_op and consumption_value_go is not None:
            threshold_bytes = int(float(consumption_value_go) * 1024 * 1024 * 1024)
            if consumption_op not in ("sup", "inf"):
                raise ValueError("Le filtre de consommation doit être 'sup' ou 'inf'.")

        # nb page min = 1
        page = max(int(page or 1), 1)
        # nb ligne min = 1
        per_page = max(int(per_page or 20), 1)
        # nb de ligne à ignorer
        offset = (page - 1) * per_page

        # etu spécifié
        if etu is not None:
            # requete après GROUP BY
            having_clause = ""
            # parametres du GROUP BY
            having_params = []
            if threshold_bytes is not None:
                operator = ">" if consumption_op == "sup" else "<"
                having_clause = f" HAVING SUM(quota_consomme) {operator} %s"
                having_params.append(threshold_bytes)

            query = f"""
                WITH filtered AS (
                    SELECT
                        etu,
                        SUM(quota_consomme)::BIGINT AS quota_consomme,
                        MIN(date_consommation) AS premiere_consommation,
                        MAX(date_consommation) AS derniere_consommation,
                        COUNT(*) AS nb_lignes
                    FROM histo_quota
                    {where_clause}
                    GROUP BY etu
                    {having_clause}
                )
                SELECT
                    *,
                    -- pour avoir le nombre total de resultats avant pagination
                    COUNT(*) OVER() AS total_rows
                FROM filtered
                ORDER BY etu ASC
                LIMIT %s OFFSET %s
            """
            query_params = params + having_params + [per_page, offset]
        # etu non spécifié
        else:
            # reprend les flitres de depart
            raw_where_clause = where_clause
            raw_params = list(params)
            if threshold_bytes is not None:
                operator = ">" if consumption_op == "sup" else "<"
                if raw_where_clause:
                    raw_where_clause += f" AND quota_consomme {operator} %s"
                else:
                    raw_where_clause = f" WHERE quota_consomme {operator} %s"
                raw_params.append(threshold_bytes)

            query = f"""
                WITH filtered AS (
                    SELECT
                        id,
                        etu,
                        quota_consomme,
                        date_consommation
                    FROM histo_quota
                    {raw_where_clause}
                )
                SELECT
                    *,
                    COUNT(*) OVER() AS total_rows
                FROM filtered
                ORDER BY date_consommation DESC, id DESC
                LIMIT %s OFFSET %s
            """
            query_params = raw_params + [per_page, offset]

        cur.execute(query, query_params)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


def get_histo_quota_kpis(reference_day=None):
    """
    Calcule les KPI sur le jour précédent.

    KPI retournés:
    - consommation_totale_jour_precedentwhere_clause
    - nombre_etu_plus_de_2go_jour_precedent
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # reference_day: jour précédent ou jour spécifié
        if reference_day is None:
            reference_day = date.today() - timedelta(days=1)
        elif isinstance(reference_day, str):
            reference_day = date.fromisoformat(reference_day)

        # Crée le début de la journée à 00:00:00
        day_start = datetime.combine(reference_day, datetime.min.time())
        # +1 = jour suivant
        day_end = day_start + timedelta(days=1)

        # Consommation totale du jour
        cur.execute(
            """
            SELECT COALESCE(SUM(quota_consomme), 0) AS total
            FROM histo_quota
            WHERE date_consommation >= %s
              AND date_consommation < %s
            """,
            (day_start, day_end),
        )
        total_row = cur.fetchone() or {"total": 0}

        # nombre d'etudiant ayant dépassé 2Go
        cur.execute(
            """
            SELECT COUNT(*) AS count_etu
            FROM (
                SELECT etu, SUM(quota_consomme) AS total_etu
                FROM histo_quota
                WHERE date_consommation >= %s
                  AND date_consommation < %s
                GROUP BY etu
                HAVING SUM(quota_consomme) > %s
            ) AS etu_over_limit
            """,
            (day_start, day_end, GB_2_BYTES),
        )
        count_row = cur.fetchone() or {"count_etu": 0}

        return {
            "date_reference": reference_day.isoformat(),
            "consommation_totale_jour_precedent": int(total_row["total"] or 0),
            "nombre_etu_plus_de_2go_jour_precedent": int(count_row["count_etu"] or 0),
            "seuil_2go_bytes": GB_2_BYTES,
        }
    finally:
        cur.close()
        conn.close()
